## Context

See proposal.md - Why, and `docs/event-delivery-design.md` for the model and the patterns compared. Facts this design depends on (backend `main` at `f0a69b34`, specification at `22967402`):

- **Publishing today**: 31 announcements. 27 are made by usecases after a repository call through `usecase.EventPublisher.PublishEvent` (`internal/usecase/event_publisher.go`), 3 by `userUseCase.publishEvent` (`user_uc.go:421`), and 2 by the identity provider webhooks (`adapter/webhook/login_event_handler.go:221`, `passkey_event_handler.go:172`). Most failures are logged and dropped. The payloads are the structs of `internal/entity/event_data.go`, JSON-encoded by `messaging.NewEvent` (`infrastructure/messaging/cloudevents.go`), whose id is a UUIDv5 named after the workflow step and a per-step counter inside a workflow and after a random value elsewhere.
- **Watermill** v1.5.3 with watermill-nats v2.2.0. The NATS publisher sets `JetStreamConfig.TrackMsgID: true` (`messaging/publisher.go`), so the message UUID is sent as `Nats-Msg-Id`. JetStream consumers redeliver without limit (`maxDeliver: -1` in `cloud-provisioning/k8s/namespaces/nats/base/jetstream/consumer-*.yaml`).
- **watermill-sql v4.1.5** (not a dependency yet):
  - `NewPublisher` takes a transaction (`TxFromPgx(pgx.Tx)` adapts ours).
  - `Publish(topic, msgs...)` writes one multi-row `INSERT`.
  - `PostgreSQLQueueSchema` reads `WHERE acked = false ORDER BY offset LIMIT n FOR UPDATE`: a row of a transaction still open is not visible yet and is read once committed, so none is skipped. With `PostgreSQLQueueOffsetsAdapter{DeleteOnAck: true}` an acknowledged row is deleted (`queue_offsets_adapter_postgresql.go`). `GeneratePayloadType` can make the payload column BYTEA.
- **Watermill forwarder** (`components/forwarder`): a publisher wrapper writes each message, wrapped in an envelope with its destination topic, to one forwarder topic. The `Forwarder` subscribes to that topic and publishes each message to its destination with the original UUID and metadata. The envelope is JSON (`DefaultMarshaler`).
- **DBOS Transact Go v1.7.0**:
  - The system tables are in the application database, schema `dbos` (`infrastructure/workflow/runtime.go`).
  - A workflow id starts at most one workflow.
- **Entity operations that cannot tell "changed" from "already done" today**:

  | Operation | Where | What it does now |
  |---|---|---|
  | Follow.Unfollow | `follow_repo.go:92` | ignores the rows affected |
  | Follow.SetHype | `follow_repo.go:33-37` | no `hype <> $3` guard |
  | PushSubscription.Create | `push_subscription_repo.go:19-27` | upserts |
  | PushSubscription.Delete | `push_subscription_repo.go:97` | ignores the rows affected |
  | LotteryEntry.PersistDrawOutcome | `lottery_entry_repo.go:94-103` | no state guard |
  | ResaleListing.RecordRefund | `resale_listing_repo.go:187-203` | returns nil in both cases |
  | SeriesImage.Create | `series_repo.go:161-165` | `DO NOTHING`, rows ignored |
  | Notification.UpdateDelivery | `notification_repo.go:104` | ignores the rows affected |
  | TicketJourney.Upsert | `ticket_journey_repo.go:95` | ignores the rows affected |
  | Artist.Create | `artist_repo` | `DO NOTHING`, returns existing artists too |

- `entity/v1.User` carries `full_name` (10) and `phone_number` (11).
- `LotteryEntry` has no lost reason: a capture failure is only in the `CaptureFailed` field of the hand-written payload (`entity/event_data.go`). Its sale and its referral code are handled by `remodel-ticket-sales`, which this change follows: the entry names its sale and its Order, and the referral code moves to the Order.

## Goals / Non-Goals

**Goals:**
- One way to announce, one way to request work, one id rule, no announcement lost or repeated by a retry.
- Usecases free of messaging code; the announcing operation named in its Go doc and its spec.

**Non-Goals:**
- `users.name` (out of scope, decided 2026-10-28).
- Ordering across subjects. Receivers do not rely on order today and keep not relying on it.
- Exactly-once side effects in receivers beyond what they do today (their own send times and unique keys).

## Decisions

### One outbox table through the forwarder

```
repository method (one pgx transaction)
  change rows ... if changed:
    outbox.Record(ctx, tx, subject, protoMessage)
      -> forwarder.Publisher{ForwarderTopic: "events_outbox"}
         -> watermill-sql Publisher on TxFromPgx(tx)   (one INSERT, multi-row for many)
commit
workflow-worker: forwarder.Forwarder
  subscribes watermill-sql "events_outbox" -> publishes to the NATS publisher (TrackMsgID)
```

- The forwarder sends every subject through one table (`watermill_events_outbox`). Per-subject tables would need a subscriber per subject and a migration for every new subject.
- The table uses `PostgreSQLQueueSchema` with `PostgreSQLQueueOffsetsAdapter{DeleteOnAck: true}`: a row is deleted as soon as the forwarder has published it and JetStream acknowledged it. No offsets table, no retention schedule, and no ordering is promised (receivers do not need it). The alternative, the ordered `PostgreSQLSchema` with an offsets table and a scheduled delete below the offset, keeps every delivered row until the delete runs and needs that schedule.
- The envelope is the forwarder's default JSON, so the payload column keeps the watermill default (JSON). The binary proto payload is base64 inside it. Measured for one LotteryEntry: a 622 B row built in 3.9 us, of which 416 B and 3.2 us are the envelope and the CloudEvents and trace metadata that a row would carry anyway. The row lives only until it is delivered, and the message on the stream is the binary proto (156 B). Rejected: a msgpack envelope marshaler (about 500 B and 1-2 us per row) for an extra dependency on a copy that lives seconds.
- The table is created by an Atlas migration (watermill-sql forbids auto-initialisation on a transaction), with the default batch size and a subscriber in the worker only. The forwarder sets `AckWhenCannotUnwrap: true`, logging the row: an envelope that cannot be read never succeeds. Any other failure to publish keeps the row and is retried; the undelivered-age alert reports a row stuck for 10 minutes. No dead-letter table.
- An operation announcing many entities (PersistDrawOutcome) builds and inserts the messages in chunks of a few thousand within its one transaction, never all of them in memory at once.
- `outbox.Record` lives in `infrastructure/messaging`. It builds the message the way `NewEvent` does:
  - id: a UUIDv7 made at that moment;
  - metadata: CloudEvents `ce_id` (the id), `ce_time` (now), `ce_type` (the subject) and `ce_datacontenttype: application/protobuf`;
  - the caller's trace context in the metadata, which the forwarder keeps.

  `eventID`, `WithPublishOrigin`, the UUIDv5 namespace and the step origin set by `Flow.Step` go.
- The forwarder runs in `workflow-worker` (1 replica), next to the DBOS runtime.

### Entity operations announce; usecases do not

- Each announcing repository method takes the outbox in its constructor and calls `Record` on its own transaction after the change, only when the change happened (rows affected, the returned outcome, or a guarded `UPDATE ... WHERE <state>`). The ten operations in Context gain the guard or read their rows affected.
- Each announcing method's Go doc gets an `# Announces` section: the subject, the entity in the payload, and when nothing is announced. Each has a repository contract test: one outbox row on a change, none on no change, nothing stored when the outbox insert fails.
- `usecase.EventPublisher` and its mock are deleted. The usecase constructors lose the publisher, so an announcement outside an entity operation does not compile.
- A workflow step that runs again after its operation committed finds the change made: no `dbos.RunAsTransaction`, no step-derived id.

### Payload: the entity's proto, converted in `internal/adapter/pb`

- `internal/adapter/rpc/mapper` moves to `internal/adapter/pb`. Functions are renamed `pb.From<Entity>` (entity to proto) and `pb.To<Entity>` (proto to entity), and every caller is updated. `proto` was rejected as a package name: the same files import `google.golang.org/protobuf/proto`. The infrastructure layer imports `pb`; nothing forbids it, and the dependency points inward.
- Payloads are `proto.Marshal` of the entity message after the change. A User payload clears `full_name` and `phone_number` (`pb.FromUserForAnnouncement`, one function, covered by a test).
- The structs of `entity/event_data.go` go; the subject constants and `AllSubjects` stay. Receivers unmarshal the entity message and convert it with `pb.To<Entity>`, or read the fields they need.
- **The entity proto does not depend on screens.** A field absent from the proto is added unless it is personal data that must be protected:
  - `LotteryEntry` gains `lost_reason` (`LOTTERY_ENTRY_LOST_REASON_NOT_DRAWN`, `..._CARD_NOT_CHARGED`).
  - `User` gains `last_login_time`.
  - `Artist` gains `organizer_id`, the Organizer that represents it (at most one: `organizer_artists.artist_id` is unique); the entity Purpose draws Organizer ||--o{ Artist (decided 2026-10-28).
  - `Passkey` gains `name`.
  - `PushSubscription` gains `device_family`, derived from the push address. The announcement clears `endpoint` and `keys` (`pb.FromPushSubscriptionForAnnouncement`).
  - The audit compares every entity struct with its proto message and adds what is missing in the same proto release.

### Requests start workflows

A request for one receiver with no stored change behind it starts that receiver's workflow through `usecase.Workflows.Start` (or `Flow.Start` inside a workflow), named after the business key of the request. Work that follows a change stored outside a workflow runs from that change's announcement (the cover image: SeriesImage.Create announces SERIES_IMAGE.uploaded). This holds inside a workflow too: a workflow that stores a change for many entities does not start the follow-up work per entity, because each `Flow.Start` is one checkpoint write in the parent workflow, one after another (1,000,000 entries, 1,000,000 writes). The operation's announcements are written in one transaction, and the consumer starts one workflow per entity under its business key (the lottery draw: the consumer of each Won entry starts `issue:<entry>`, of each Lost entry `release:<entry>`). The NATS subjects of the requests and their durable consumers go. DBOS `WithEnqueueTransaction` is not needed.

| Request | Started by | Workflow | Workflow id (business key) | Follows a stored change |
|---|---|---|---|---|
| New concerts for a follower | NotificationUseCase.NotifyNewConcerts (receiver of CONCERT.created) | NotificationUseCase.Deliver | `deliver:new_concerts:<user>:<announcement id>`; an admin's direct call uses its own call id | no |
| A discovered sale for a recipient | TicketSaleAnnouncementUseCase.AnnounceDiscoveredSale | NotificationUseCase.Deliver | `deliver:ticket_sale:<user>:<ticket sale>` | no |
| The push of an Order's confirmation | NotificationUseCase.SendOrderConfirmation (receiver of ORDER.paid), after its email | NotificationUseCase.Deliver | `deliver:order_confirmation:<order>`, so a repeated announcement pushes once while the email is kept to one by `orders.confirmation_send_at` | yes (the push follows the paid Order, but runs in the receiver of its announcement) |
| A due reminder stage | TicketSaleReminderUseCase.ScanDueReminders | TicketSaleReminderDeliveryUseCase.DeliverReminder | `reminder:<user>:<ticket sale>:<stage>:<15-minute scan period>`, so a later scan can retry a failed push | no |
| A verification email resend | UserUseCase.ResendEmailVerification | UserUseCase.ReissueEmailVerification | a UUIDv7 per allowed call (the call is the request) | no |
| A passkey recovery link | UserUseCase.RequestPasskeyRecovery | UserUseCase.SendPasskeyRecoveryLink | a UUIDv7 per allowed request | no |
| Ingesting found concerts | ConcertUseCase.SearchNewConcerts and SearchNewConcertsOnFirstFollow | ConcertCreationUseCase.CreateFromDiscovered, the found series as input | `ingest:<artist>:<search time>` | no |
| Recording a passkey notice | the passkey webhook | PasskeyUseCase.RecordChange | `passkey:<provider passkey id>:<added or removed>` | no |

- SeriesImage gains the Series it was uploaded for (`series_images.series_id`), which its processing reads from the announcement.
- `CreateFromDiscovered` stores the events it publishes for one series in one `Concert.Create` call, so one series yields one announcement per newly listed Artist, as the per-series announcement did before.

### Observations from outside become facts

- **Passkey webhook**: it starts `PasskeyUseCase.RecordChange` as a workflow (id in the requests table) and answers 500 when it cannot. A workflow, not a synchronous call, because the identity provider does not redeliver its notices and a sign-up passkey must wait up to 10 minutes for its User. `Passkey.Create` and `Passkey.Delete` gain the guard (`ON CONFLICT DO NOTHING` rows affected, `DELETE ... RETURNING`) and announce `USER.passkey_added` or `USER.passkey_removed` with the Passkey when they change something. `UserUseCase.NotifyPasskeyChange` consumes both, so the sign-up passkey is now emailed as added once recorded (decided 2026-10-28). The Passkey gains `name`, the label the identity provider gave it, which the email shows as before (`passkeys.name`, proto `Passkey.name`).
- **Login webhook**: it calls `UserUseCase.RecordLogin`, which calls `User.RecordLogin`. That operation is a guarded `UPDATE users SET last_login_time = $t WHERE id = $u AND (last_login_time IS NULL OR last_login_time < $t)`, and it announces `USER.logged_in` with the User when a row changed. A redelivered or older notice changes nothing. The `users.last_login_time TIMESTAMPTZ` column is added by migration.

### Subjects after this change

| Subject | Announced by | Payload | Receivers |
|---|---|---|---|
| ARTIST.followed | Follow.Follow | Follow | product analytics; ConcertUseCase.SearchNewConcertsOnFirstFollow |
| ARTIST.unfollowed | Follow.Unfollow | Follow as removed | product analytics |
| ARTIST.hype_changed | Follow.SetHype | Follow | product analytics |
| ARTIST.created | Artist.Create | Artist | ArtistUseCase.ResolveCanonicalName, SyncArtistImage |
| CONCERT.created | Series.PublishEvents, Concert.Create | the Concerts listed for one Artist; `ce_subject` = the Artist id | NotificationUseCase.NotifyNewConcerts |
| SALES_PHASE.discovered | TicketSale.UpsertDiscovered | TicketSale | TicketSaleAnnouncementUseCase.AnnounceDiscoveredSale |
| SERIES_IMAGE.uploaded | SeriesImage.Create | SeriesImage, with its Series | SeriesImageUseCase.Process |
| ORDER.checkout_expired | Checkout.Release | Checkout | product analytics |
| ORDER.paid | Order.Issue | Order | product analytics, NotificationUseCase.SendOrderConfirmation, TicketJourneyUseCase.MarkPaid |
| ORDER.lottery_entry_drawn | LotteryEntry.PersistDrawOutcome | LotteryEntry, one announcement per entry | product analytics |
| ORDER.resale_listing_refunded | ResaleListing.RecordRefund | ResaleListing | NotificationUseCase.SendResaleSold |
| ORDER.ticket_admitted | Ticket.Admit | Ticket | product analytics |
| ORGANIZER.created | Organizer.CompareAndSetStatus (provisioning to active) | Organizer | product analytics |
| ORGANIZER.artist_associated | Organizer.AssociateArtist | Artist, with its new `organizer_id` | product analytics |
| NOTIFICATION.subscribed, NOTIFICATION.unsubscribed | PushSubscription.Create, PushSubscription.Delete | PushSubscription without push address and keys, with its device family | product analytics |
| NOTIFICATION.delivered | Notification.UpdateDelivery (Queued to Delivered) | Notification | product analytics |
| TICKET_JOURNEY.status_changed | TicketJourney.Upsert | TicketJourney | product analytics |
| USER.created | User.Create | User without full name and phone number | UserUseCase verification email; product analytics |
| USER.logged_in | User.RecordLogin | User without full name and phone number | product analytics |
| USER.passkey_added, USER.passkey_removed | Passkey.Create, Passkey.Delete | Passkey (as removed for a removal) | UserUseCase.NotifyPasskeyChange |

### How each receiver drops a repeat

JetStream drops a repeated id for 2 minutes only; a delivery repeated later (a forwarder that stopped between publish and ack) reaches the receiver. Every receiver with a side effect names its own guard:

| Receiver | Guard |
|---|---|
| product analytics | PostHog's event `uuid` = the announcement id |
| NotifyNewConcerts, AnnounceDiscoveredSale | the started Deliver workflow's id |
| SendOrderConfirmation | `orders.confirmation_send_at` for the email, the started Deliver workflow's id for the push |
| SendResaleSold | the sold email send time |
| SendLotteryLoss (later change) | `lottery_entries.loss_email_send_at` |
| MarkPaid, ResolveCanonicalName, SyncArtistImage, SeriesImageUseCase.Process | the result is the same when repeated |
| SearchNewConcertsOnFirstFollow | the Artist's ConcertSearch record |
| UserUseCase.NotifyPasskeyChange, the verification email on USER.created | no record of their own (a removed Passkey has no row): the receiver starts a workflow named after the announcement id, `notify:<announcement id>`, and the email is sent in it |

A receiver added later picks one of these guards; task 10.1 tests "Delivered twice" for each.

- Removed subjects: NOTIFICATION.requested, SALES_PHASE.reminder_due, USER.email_verification_resend_requested, USER.passkey_recovery_requested and CONCERT.discovered (now workflows); CONCERT.cancelled and ORGANIZER.concert_published (no receiver); USER.passkey_changed (split into added and removed, because the Passkey payload cannot say which).
- **A payload is the entities one operation changed together, of one type** (`entity/v1` messages; one entity unless the receiver needs them together, as for CONCERT.created). A list payload is a message with one `repeated` field of the entity, declared next to the entity in `entity/v1` (`ConcertList`). What the announcement is about, when the payload does not say it, goes in the CloudEvents `subject` attribute.
- Receivers needing a value that is not on the entity read it by id (the confirmation email reads the Order's Event and Tickets; the lottery result reads the entry's Order for its TicketStock). The previous level or status of a hype or journey signal is the fan's previous signal, as the hype signal already defines.

### LotteryEntry: lost reason

- `lottery_entries.lost_reason SMALLINT` is NULL unless Lost: 1 = not drawn, 2 = card could not be charged. The proto enum `LotteryEntryLostReason` uses the same numbers; `0` (`..._UNSPECIFIED`) is never stored and maps to NULL. A check constraint ties it to the state. Existing Lost rows are backfilled as not drawn, because the capture failure was never stored. The count is checked read-only in prod before the migration (expected 0).
- `PersistDrawOutcome` takes the lost reason per loser. It already leaves an entry that is no longer Entered unchanged (`remodel-ticket-sales`, which drops the draw time), and announces only the entries it changes, so a second call changes and announces nothing.

### Undelivered announcements

The existing `report-workflows-needing-admin` schedule (every 5 minutes) also reads the age of the oldest row in `watermill_events_outbox` (rows are deleted when delivered). It sets a gauge `event_delivery.oldest_undelivered_age_seconds`, and a Cloud Monitoring alert fires above 600 s. One mechanism, next to the workflow alert.

### Receivers during the switch

Receivers decode by `ce_datacontenttype`: `application/protobuf` with the new decoder, `application/json` with the old structs, for one release. The JSON path and the old structs are deleted once prod shows no JSON message left on any stream (stream `last_seq` older than the switch). The product has no users, so the window is short.

## Risks / Trade-offs

- [Every announcing write now fails when the outbox insert fails, where a publish failure was ignored before] → The insert is in the same database as the write. It fails only when the write itself would. This is the point of the change.
- [The forwarder is a single consumer in one replica] → A stopped worker delays delivery and does not lose it. The 10-minute alert reports a delay.
- [Behaviour seen in product analytics changes (no signal for repeated hype levels, unfollows of artists not followed, repeated subscriptions, repeated charge notices)] → Intended (proposal **BREAKING**). Dashboards counting those repeats are checked in the release task.
- [A receiver's side effect is not idempotent] → Unchanged from today: every receiver already treats a repeated announcement as one (send times, unique keys). The spec "delivered twice" scenario is tested per receiver that has one.
- [One forwarder publishes one message at a time] → 1,000,000 announcements of one draw may take more than 10 minutes to deliver and trip the alert. The charges of the same draw (queue concurrency 2, one Stripe call each) take far longer, so the forwarder is not what fans wait for. The outbox is one table read in insertion order, so announcements recorded after the draw (a sign-up's verification email, a first-come Order's confirmation) wait behind it for that time too. With no users this is accepted; if task 11.2 shows it, the forwarder publishes asynchronously or the draw's announcements get a table of their own. Task 11.2 measures the delivery rate; the alert threshold or the forwarder's concurrency is revisited only if a real sale gets near that size.
- [A row lives in the outbox until delivered] → Rows are deleted on delivery. 1,000,000 rows is about 620 MB while a large draw is being delivered.

## Migration Plan

0. `remodel-ticket-sales` is released first; this change is planned on its model, and `make-lottery-draw-durable`, `unify-order-issuance` and `resell-tickets-by-lottery` follow this change.
1. specification: proto release with `LotteryEntry.lost_reason`, `User.last_login_time`, and the fields from the audit.
2. backend refactor PR: move `adapter/rpc/mapper` to `adapter/pb` with the new names (no behaviour change).
3. Read-only in prod: count Lost lottery entries and outbox prerequisites. Record the result here.
4. backend PR:
   - the migrations (the outbox table, `series_images.series_id`, `lottery_entries.lost_reason`, `users.last_login_time`);
   - the outbox and the forwarder;
   - the entity operations;
   - the usecases without the publisher;
   - the request workflows;
   - the webhooks;
   - receivers decoding both formats;
   - the alert gauge.
5. cloud-provisioning PR: the alert policy. The durable consumers and stream subjects of the removed subjects (`NOTIFICATION.requested`, `SALES_PHASE.reminder_due`, `USER.email_verification_resend_requested`, `USER.passkey_recovery_requested`, `CONCERT.discovered`, `CONCERT.cancelled`, `ORGANIZER.concert_published`) are deleted after step 4 is live.
6. backend PR: delete the JSON decoding and `event_data.go` payload structs.

Rollback: revert the backend release. Announcements still in the outbox are not delivered by the old code; with no users this loses at most the analytics of the rollback window. The new columns stay unused.
