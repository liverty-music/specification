## 1. Prerequisites

- [ ] 1.0 Confirm `remodel-ticket-sales` is released in backend and archived (this change's deltas of `persist-draw-outcome`, `run-draw`, `order/issue`, `checkout/release` and `release-expired` are written against the main specs as it leaves them); verify `openspec validate publish-events-through-outbox --strict` passes with no archive refusal
- [ ] 1.1 Read-only in prod (cloud-provisioning runbook, ephemeral `db-proxy`): count Lost `lottery_entries`, `passkeys` rows and `organizer_artists` rows, and record the counts in design.md "Migration Plan"; verify the counts are recorded

## 2. Proto (specification; components/entity/lottery-entry, user, artist, passkey Purposes)

- [ ] 2.1 Add `LotteryEntry.lost_reason` (enum `LotteryEntryLostReason`; the sale and the Order come from `remodel-ticket-sales`), `User.last_login_time`, `Artist.organizer_id`, `Passkey.name` and `user_id`, `SeriesImage.series_id`, `PushSubscription.device_family`, the `Follow` message (`user_id`, `artist_id`, `hype`) and the list message `ConcertList`; verify `buf lint`, `buf format` and `buf breaking` pass
- [ ] 2.2 Compare every struct in backend `internal/entity` with its `entity/v1` message and add each field left out for no personal-data reason; record the list in the PR description; verify `buf lint` passes
- [ ] 2.3 Merge, cut the specification release, and confirm `buf-release.yml` succeeds and the BSR packages carry the new fields

## 3. Conversion package (backend refactor, no behaviour change)

- [ ] 3.1 Move `internal/adapter/rpc/mapper` to `internal/adapter/pb`, renaming functions to `pb.From<Entity>` (entity to proto) and `pb.To<Entity>` (proto to entity), and update every caller; verify `make check` passes with no reference to the old package
- [ ] 3.2 Map the fields added in 2.1 and 2.2 in `pb`, and add `pb.FromUserForAnnouncement` (clears full name, phone number and display name) and `pb.FromPushSubscriptionForAnnouncement` (clears push address and keys); verify unit tests for each mapping and each clearing pass

## 4. Event delivery (components/infrastructure/backend/process/event-delivery, durable-workflows)

- [ ] 4.1 Add the Atlas migration for the watermill-sql `events_outbox` table (`PostgreSQLQueueSchema`, JSON payload column), with column comments; verify `make lint-schema` passes and the migration applies to a local database
- [ ] 4.2 Add `messaging.Outbox.Record(ctx, tx, subject, proto.Message, ...opts)`: UUIDv7 id, CloudEvents metadata (`ce_id`, `ce_time`, `ce_type`, `ce_datacontenttype: application/protobuf`, optional `ce_subject`), trace context, written through the forwarder publisher on `TxFromPgx(tx)`; verify unit tests: one row per call, the id equals `ce_id`, a list call writes one multi-row insert
- [ ] 4.3 Run the watermill `Forwarder` from `events_outbox` (queue subscriber, `DeleteOnAck: true`, `AckWhenCannotUnwrap: true`) to the NATS publisher in `workflow-worker`; verify that a delivered row is deleted, and an integration test against local Postgres and NATS: "Change and announcement together", "Process stops before delivery" (stop the forwarder after the insert, start it, the message arrives) and "Delivered twice" (the redelivery has the same `Nats-Msg-Id` and JetStream stores one message); and a test that every subject in `entity.AllSubjects` matches a stream subject declared in cloud-provisioning `k8s/namespaces/nats/base/jetstream/stream-*.yaml` (read from a checked-in list), so no announcement is recorded for a subject no stream captures
- [ ] 4.4 Remove `eventID`, `WithPublishOrigin`, the UUIDv5 namespace and the step origin set by `Flow.Step`; verify `make check` passes and no reference is left
- [ ] 4.5 Report the age of the oldest `events_outbox` row as the gauge `event_delivery.oldest_undelivered_age_seconds` from the `report-workflows-needing-admin` schedule; verify a unit test for "Broker unreachable" (a row 11 minutes old sets the gauge above 600)

## 5. Schema for new entity state

- [ ] 5.1 Migrations: `lottery_entries.lost_reason` (SMALLINT, check tied to state, backfill not drawn), `users.last_login_time`, `passkeys.name`, `series_images.series_id`, each commented; verify `make lint-schema` passes and the migrations apply to a local database with sample rows
- [ ] 5.2 Add the attributes to the entity structs (`LotteryEntry.LostReason`, `User.LastLoginTime`, `Artist.OrganizerID`, `Passkey.Name`, `SeriesImage.SeriesID`); verify the existing entity and repository tests pass with the new fields

## 6. Entity operations announce (one contract test per scenario of each listed spec, against local Postgres, asserting the outbox rows)

- [ ] 6.1 Follow.Follow, Follow.Unfollow (read rows affected), Follow.SetHype (guard `hype <> $3`); verify every scenario of `entity/follow/follow`, `follow/unfollow` and `follow/set-hype`
- [ ] 6.2 Checkout.Release, Ticket.Admit, TicketJourney.Upsert (read rows affected), Notification.UpdateDelivery (Queued only); verify every scenario of `entity/checkout/release`, `ticket/admit`, `ticket-journey/upsert` and `notification/update-delivery`
- [ ] 6.3 PushSubscription.Create (changes only on a new address, new keys or new owner) and PushSubscription.Delete (rows affected), announcing without push address and keys; verify every scenario of `entity/push-subscription/create` and `push-subscription/delete`, and "New push subscription announced"
- [ ] 6.4 Organizer.CompareAndSetStatus (provisioning to active only) and Organizer.AssociateArtist (announces the Artist with its organizer); verify every scenario of `entity/organizer/compare-and-set-status` and `organizer/associate-artist`
- [ ] 6.5 Series.PublishEvents and Concert.Create announce `ConcertList` per Artist with `ce_subject`; verify every scenario of `entity/series/publish-events` and `concert/create`
- [ ] 6.6 Artist.Create (only inserted artists, also under a race on one MBID) and TicketSale.UpsertDiscovered (Inserted only); verify every scenario of `entity/artist/create` and `ticket-sale/upsert-discovered`
- [ ] 6.7 SeriesImage.Create stores the Series and announces SERIES_IMAGE.uploaded (rows affected); verify every scenario of `entity/series-image/create`
- [ ] 6.8 Order.Issue announces ORDER.paid; verify every scenario of `entity/order/issue`
- [ ] 6.9 LotteryEntry.PersistDrawOutcome (lost reason per loser, no announcement for an entry left unchanged, one announcement per changed entry, inserted in chunks); verify every scenario of `entity/lottery-entry/persist-draw-outcome`, and a test drawing 100,000 local entries in one call with the process heap below 200 MB
- [ ] 6.10 ResaleListing.RecordRefund (announces only when it sets the refund) and ResaleListing.ListSoldUnrefunded (refund time only); verify every scenario of `entity/resale-listing/record-refund` and `resale-listing/list-sold-unrefunded`
- [ ] 6.11 User.Create (User without full name, phone number and display name), User.RecordLogin (new, guarded update), Passkey.Create (stores name; rows affected) and Passkey.Delete (`DELETE ... RETURNING`), announcing USER.created, USER.logged_in, USER.passkey_added and USER.passkey_removed; verify every scenario of `entity/user/create`, `user/record-login`, `passkey/create` and `passkey/delete`
- [ ] 6.12 Add the `# Announces` Go doc section to every announcing method in `internal/entity`; verify `make check` passes and a grep finds one section per announcing method

## 7. Usecases stop announcing (one unit test per scenario, operations mocked)

- [ ] 7.1 Delete `usecase.EventPublisher`, its mock and the publisher argument of every usecase constructor and of `deliverNotification`; verify `make check` passes with no reference left
- [ ] 7.2 Follow, Unfollow, SetHype, ReleaseExpired, PushSubscription Create and Delete, Admit, SetStatus (no prior read), MarkPaid; verify every scenario of `usecase/follow/follow`, `follow/unfollow`, `follow/set-hype`, `checkout/release-expired`, `push-subscription/create`, `push-subscription/delete`, `ticket/admit`, `ticket-journey/set-status` and `ticket-journey/mark-paid`
- [ ] 7.3 OrganizerUseCase.Create, ReconcileProvisioning and AssociateArtist; verify every scenario of `usecase/organizer/create`, `organizer/reconcile-provisioning` and `organizer/associate-artist`
- [ ] 7.4 SeriesUseCase.Publish, Cancel and SetCoverImage, ConcertCandidateUseCase.Approve, ArtistUseCase.Search, ListSimilar and ListTop, TicketSaleDiscoveryUseCase.DiscoverForArtist; verify every scenario of `usecase/series/publish`, `series/cancel`, `series/set-cover-image`, `concert-candidate/approve`, `artist/search`, `artist/list-similar`, `artist/list-top` and `ticket-sale/discover-for-artist`
- [ ] 7.5 OrderUseCase.FulfillPayment, LotteryEntryUseCase.RunDraw (lost reasons), ResaleListingUseCase.RefundSold, UserUseCase.Create; verify every scenario of `usecase/order/fulfill-payment`, `lottery-entry/run-draw`, `resale-listing/refund-sold` and `user/create`

## 8. Requests start workflows (design "Requests start workflows")

- [ ] 8.1 Register NotificationUseCase.Deliver, TicketSaleReminderDeliveryUseCase.DeliverReminder, UserUseCase.ReissueEmailVerification, UserUseCase.SendPasskeyRecoveryLink, ConcertCreationUseCase.CreateFromDiscovered, PasskeyUseCase.RecordChange, and the email steps of NotifyPasskeyChange and of the verification email, as workflows in `cmd/worker`, with the ids of the requests table; verify `make check` passes and `/worker workflow list` shows them in a local run
- [ ] 8.2 NotifyNewConcerts, AnnounceDiscoveredSale and SendOrderConfirmation start Deliver; Deliver runs as a workflow; verify every scenario of `usecase/notification/notify-new-concerts`, `ticket-sale/announce-discovered-sale`, `notification/send-order-confirmation` and `notification/deliver`
- [ ] 8.3 ScanDueReminders starts DeliverReminder; verify every scenario of `usecase/ticket-sale/scan-due-reminders` and `ticket-sale-reminder/deliver-reminder`
- [ ] 8.4 ResendEmailVerification and RequestPasskeyRecovery start their workflows; verify every scenario of `usecase/user/resend-email-verification`, `user/reissue-email-verification`, `user/request-passkey-recovery`, `user/send-passkey-recovery-link` and `adapter/fan/api/rpc/user` "ResendEmailVerification is decided by the usecase"
- [ ] 8.5 SearchNewConcerts and SearchNewConcertsOnFirstFollow start CreateFromDiscovered, which stores one series' events in one Concert.Create call; SeriesImageUseCase.Process runs from SERIES_IMAGE.uploaded; verify every scenario of `usecase/concert/search-new-concerts`, `concert/search-new-concerts-on-first-follow`, `concert/create-from-discovered` and `series-image/process`

## 9. Observations from outside (passkey and login webhooks)

- [ ] 9.1 The passkey webhook starts PasskeyUseCase.RecordChange; RecordChange stores or deletes the Passkey with its name and stops 10 minutes after its first run; NotifyPasskeyChange runs on USER.passkey_added and USER.passkey_removed and sends in a workflow named after the announcement id; verify every scenario of `adapter/fan/api/webhook/passkey-events`, `usecase/passkey/record-change` and `usecase/user/notify-passkey-change`
- [ ] 9.2 The login webhook calls UserUseCase.RecordLogin; verify every scenario of `adapter/fan/api/webhook/login-events` and `usecase/user/record-login`

## 10. Receivers read protobuf payloads

- [ ] 10.1 Every remaining receiver decodes by `ce_datacontenttype` (protobuf, or the old JSON for one release), reads values not on the entity by id, and uses the guard of design "How each receiver drops a repeat" (the verification email on USER.created moves into a workflow named after the announcement id); verify one unit test per receiver for each format, and "Delivered twice" per receiver that has a side effect
- [ ] 10.2 The analytics consumer maps each announcement to its catalogue event, with the previous hype level or journey status taken from the fan's previous signal; verify unit tests per mapped subject

## 11. Release (backend and cloud-provisioning)

- [ ] 11.1 Run `make test-stripe-e2e` with the Stripe Sandbox key and confirm the checkout and lottery legs pass with Order.Issue announcing
- [ ] 11.2 Merge the backend PR, cut the release, and confirm in prod (read-only) that the AtlasMigrations applied, `workflow-worker` rolled out and its forwarder runs, a follow made in prod reaches product analytics once and leaves no `events_outbox` row; record the forwarder's delivery rate (messages per second, from a local run of 100,000 announcements) in design.md "Risks"
- [ ] 11.3 cloud-provisioning PR: the alert policy on `event_delivery.oldest_undelivered_age_seconds` above 600 s in the Pulumi program, and deletion of the durable consumers and stream subjects of the removed subjects (design "Subjects after this change") and of USER.passkey_changed, with consumers for USER.passkey_added and USER.passkey_removed; verify `pulumi preview` shows only these and, after merge, the prod stream config matches
- [ ] 11.4 Run `gh workflow run stripe-sandbox-e2e.yml` in backend and confirm the run succeeds

## 12. Remove the JSON payloads

- [ ] 12.1 Confirm read-only in prod that no stream holds a JSON message published before the release, then delete the JSON decoding and the payload structs of `entity/event_data.go`; verify `make check` passes and no struct is left

## 13. Archive

- [ ] 13.1 Edit the main spec Purposes this change lists:
  - entity Purposes: `components/entity/lottery-entry` gains lost reason (not drawn, or card could not be charged); `user` gains last login time; `series-image` gains series; `artist` gains organizer, with Organizer ||--o{ Artist; `passkey` gains name.
  - usecase and adapter Purposes that still say "announce": `usecase/order/fulfill-payment`, `follow/follow`, `follow/unfollow`, `push-subscription/delete`, `ticket-journey/set-status`, `user/reissue-email-verification`, `user/send-passkey-recovery-link`, `series-image/process`, `concert/create-from-discovered`, `concert/search-new-concerts`, `ticket-sale/discover-for-artist`, `resale-listing/refund-sold`, `entity/resale-listing/list-sold-unrefunded`, and `adapter/fan/api/webhook/passkey-events`.

  Verify `openspec validate --specs` passes.
- [ ] 13.2 Update backend `AGENTS.md` (entity operations announce through the outbox, the `# Announces` section, no publisher in usecases, requests start workflows) and `docs/event-delivery-design.md` (status: implemented); verify both PRs merge
- [ ] 13.3 Before archiving, confirm `make-lottery-draw-durable`, `unify-order-issuance` and `resell-tickets-by-lottery` are still written on this change (no usecase announcement, no step-derived event id, work after a stored change started from its announcement); verify `openspec validate <change> --strict` passes for each
