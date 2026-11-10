## Context

See proposal.md for why. How events flow today:
- An entity operation records an announcement in the outbox (`watermill_events_outbox`) in its own transaction.
- The forwarder in workflow-worker publishes the announcement to NATS JetStream under its subject.
- Each consumer behavior in `internal/di/consumer.go` binds a pre-existing durable whose name is the behavior name. It finds the stream from the subject with `messaging.StreamForSubject`, and binds only; it never creates the durable.
- NACK owns the streams and durables (`k8s/namespaces/nats/base/jetstream/`, every CR with `preventDelete: true`). KEDA scales event-consumer on each durable's lag (`event-consumer/scaledobject.yaml`, `minReplicaCount: 1` in prod).

Facts the migration relies on:
- **NACK reconciles a Consumer CR by the pair (spec.streamName, durableName)** (`internal/controller/consumer_controller.go` at v0.25.0; the chart in use is 0.35.0 with appVersion 0.24.0):
  - When no consumer with that pair exists on the server, NACK creates one. So changing a CR's `streamName` creates the durable on the new stream and leaves the old durable in place.
  - On the same stream, a changed filter is applied with `UpdateConfiguration`.
  - A CR removed while `preventDelete: true` leaves its stream or durable in place. A CR removed with `preventDelete: false` deletes it.
- **The CRD supports `filterSubjects`** (a list) on a Consumer (`charts/nack-0.35.0/nack/crds/crds.yml:628`).
- **Unused streams and durables today**:
  - Durables: no behavior binds `track-ticket-email`.
  - Streams: no subject is published to `VENUE.*` or `TICKET_EMAIL.*`.
- **The product has no users yet**, and availability may be traded for simplicity. The dev environment is stopped, so the migration is verified in prod with read-only checks.

## Goals / Non-Goals

**Goals:**
- One name per event across the spec, the Go constant, the subject, the stream, the durable and the docs.
- One event per state where consumers react to the states differently, so each consumer subscribes to exactly what it acts on (decision 2).
- No stream, durable, CR, KEDA trigger, PostHog event name or doc left that names a retired subject.

**Non-Goals:**
- Renaming analytics events that do not come from a domain event (`notification.opened`, `concert.search.completed` and the other UI or processing events).
- Renaming behaviors whose names describe what they do rather than an event (`send-lottery-loss`, `start-resale-entry-workflow`).
- Changing payloads. Each event keeps the payload it carries today.

## Decisions

### 1. Names

- **Event**: `<Entity>.<What>`. When the event tells that the entity entered a state, What is that state (Order.Paid, LotteryEntry.Won). Otherwise it is what happened to the entity, in the past tense (Follow.Created, Follow.HypeChanged, TicketJourney.StatusChanged).
- **PostHog event**: an analytics event forwarded from a domain event is named by the subject in lower case (`lottery_entry.won`, `follow.created`, `user.signed_in`). `user.created`, `order.paid`, `checkout.expired` and `ticket.admitted` keep their names. The BigQuery models that count `user.created` and `order.paid` (`mart_campaign_value.sql`) are unaffected.
- **Subject**: `<ENTITY>.<what>`, upper snake case then lower snake case (`LOTTERY_ENTRY.won`, `FOLLOW.hype_changed`). This keeps two tokens, so a stream's `<ENTITY>.*` filter matches.
- **Stream**: one per entity that has events, named `<ENTITY>`.
- **Go constant**: `Subject<Entity><What>` (`SubjectLotteryEntryWon`).
- **Spec**: a requirement says "announce the X as y (X.Y)". The parenthesis is the event name, so a reader and a grep find the same string.

| event | subject | announced by | durables (behavior) |
|---|---|---|---|
| Concert.Created | `CONCERT.created` | Concert.Create, Series.PublishEvents | notify-concert |
| Event.Cancelled | `EVENT.cancelled` | Series.CancelEvents | send-event-cancelled, end-lottery-entries-of-cancelled-event |
| Artist.Created | `ARTIST.created` | Artist.Create | refresh-artist, resolve-artist-image |
| Follow.Created | `FOLLOW.created` | Follow.Follow | search-first-followed-artist, track-follow-created |
| Follow.Removed | `FOLLOW.removed` | Follow.Unfollow | track-follow-removed |
| Follow.HypeChanged | `FOLLOW.hype_changed` | Follow.SetHype, Follow.RaiseHype | track-follow-hype-changed |
| User.Created | `USER.created` | User.Create | track-user-created, verify-user-email |
| User.SignedIn | `USER.signed_in` | User.RecordLogin | track-user-signed-in |
| Passkey.Added / Passkey.Removed | `PASSKEY.added` / `PASSKEY.removed` | Passkey.Create / Passkey.Delete | notify-passkey-added / notify-passkey-removed |
| PushSubscription.Subscribed / .Unsubscribed | `PUSH_SUBSCRIPTION.subscribed` / `.unsubscribed` | PushSubscription.Create / .Delete | track-push-subscription-subscribed / track-push-subscription-unsubscribed |
| TicketSale.Discovered | `TICKET_SALE.discovered` | TicketSale.UpsertDiscovered | notify-ticket-sale-discovered |
| TicketJourney.StatusChanged | `TICKET_JOURNEY.status_changed` | TicketJourney.Upsert, .UpsertIfReplaceable | track-ticket-journey |
| Organizer.Activated | `ORGANIZER.activated` | Organizer.CompareAndSetStatus | track-organizer-activated |
| Artist.Represented | `ARTIST.represented` | Organizer.AssociateArtist | track-artist-represented |
| SeriesImage.Uploaded | `SERIES_IMAGE.uploaded` | SeriesImage.Create | process-series-image |
| Order.Paid | `ORDER.paid` | Order.Issue | send-order-confirmation, mark-ticket-journey-paid, track-order-paid |
| Order.Refunded | `ORDER.refunded` | Order.CommitRefund | send-order-refunded |
| ResaleListing.Sold | `RESALE_LISTING.sold` | Order.Issue | start-resale-refund |
| ResaleListing.Refunded | `RESALE_LISTING.refunded` | ResaleListing.RecordRefund | send-resale-sold |
| LotteryEntry.Entered | `LOTTERY_ENTRY.entered` | LotteryEntry.Create | mark-ticket-journey-applied |
| LotteryEntry.Won | `LOTTERY_ENTRY.won` | LotteryEntry.PersistDrawOutcome | start-lottery-entry-workflow, track-lottery-entry-result |
| LotteryEntry.Lost | `LOTTERY_ENTRY.lost` | LotteryEntry.PersistDrawOutcome, .RevertWin, .EndEnteredByEvent | start-lottery-entry-workflow, send-lottery-loss, track-lottery-entry-result |
| ResaleEntry.Won, .Lapsed, .Lost, .Withdrawn | `RESALE_ENTRY.won`, `.lapsed`, `.lost`, `.withdrawn` | ResaleEntry.PersistDrawOutcome (won, lapsed, lost), .RevertWin (lost), .Withdraw (withdrawn) | start-resale-entry-workflow (all four), send-resale-entry-ended (lapsed, lost) |
| Checkout.Held | `CHECKOUT.held` | Checkout.GetOrCreateHeld | start-checkout-expiry |
| Checkout.Expired | `CHECKOUT.expired` | Checkout.Release, .GetOrCreateHeld | release-expired-checkout, track-checkout-expired |
| Checkout.Released | `CHECKOUT.released` | Checkout.GetOrCreateHeld, .RevertCommit | release-released-checkout |
| Ticket.Admitted | `TICKET.admitted` | Ticket.Admit | track-ticket-admitted |

**Renamed durables** (the old name carries a retired event name or a different prefix style):

| old name | new name |
|---|---|
| notify-sales-phase | notify-ticket-sale-discovered |
| track-artist-followed | track-follow-created |
| track-artist-unfollowed | track-follow-removed |
| track-artist-hype-changed | track-follow-hype-changed |
| track-notification-subscribed | track-push-subscription-subscribed |
| track-notification-unsubscribed | track-push-subscription-unsubscribed |
| track-user-logged-in | track-user-signed-in |
| track-lottery-entry-drawn | track-lottery-entry-result (Won and Lost) |
| analytics-organizer-created | track-organizer-activated |
| analytics-organizer-artist-associated | track-artist-represented |

Alternative considered: keep the current streams and change only the Go identifiers. It was rejected because the user asked for every layer to match. A stream named ORDER holding lottery and checkout events, or one named SALES_PHASE holding TicketSale events, is the inconsistency this change removes.

### 2. Split an event by state only where consumers react differently

An event is split into one event per state when some consumer reacts to the states differently. When every consumer treats every state the same, it stays one `StatusChanged`-style event that carries the state. Applied to the three generic events:
- **LotteryEntry (Won, Lost): split.** The workflow starter charges a Won entry and releases a Lost one, and `send-lottery-loss` acts only on Lost. Today it receives Won entries and drops them by reading the payload (`lottery_entry_drawn_consumer.go:85`).
- **ResaleEntry (Won, Lapsed, Lost, Withdrawn): split.** The workflow starter issues a Won entry and releases the others, and `send-resale-entry-ended` acts only on Lapsed and Lost, dropping the rest by payload (`resale_entry_consumer.go:28`).
- **TicketJourney: not split.** Its one consumer forwards every status the same way, as one analytics event with the status as a property. Upsert also announces when only who set the status changes, which a per-status event would misname.

The split costs no extra durable or KEDA trigger: a consumer of several states lists them (below), and a stream's `<ENTITY>.*` filter covers every subject. Checkout (Held, Expired, Released) and Order (Paid, Refunded) already follow this rule.

A durable that acts on several states of one entity subscribes with `filterSubjects`, for example `start-resale-entry-workflow` on all four ResaleEntry subjects. Its behavior table entry names that list. The subscriber finds the stream from any one of them, since they share the entity's stream. The handler tells the state from the subject, not the payload.

The other option was one durable per state (start-resale-entry-workflow-won and so on). It doubles the durables and KEDA triggers for no change in behavior.

### 3. Cut over in place, then remove what is left behind

Because NACK creates a durable when the pair (stream, durable) is new, and leaves the old one, the CRs are edited in place. No CR exists twice.

1. **cloud-provisioning PR 1**:
   - Add the new Stream CRs.
   - Edit each Consumer CR to its new `streamName` and `filterSubject`/`filterSubjects`, and rename the CRs of renamed durables.
   - Add KEDA triggers for the new (stream, durable) pairs, and keep the old triggers.

   After the sync, both the old durables (on the old streams) and the new ones exist. The running backend still binds the old ones.

   The durables that keep their stream, name and subject (on ORDER.paid, CONCERT.created, ARTIST.created, USER.created, TICKET_JOURNEY.status_changed and SERIES_IMAGE.uploaded) are not touched.
2. **Before the backend rollout**: confirm in prod that `watermill_events_outbox` is empty and that every old durable has 0 pending messages (read-only checks).
3. **backend PR**: publishes the new subjects and binds the new durables. The health check lists the new durables.
4. **After the rollout**: confirm in prod that every old durable still has 0 pending messages, and that the new ones are bound. If an old durable has a pending message, it was published by an old pod during the rollout. Republish it to its new subject with the nats CLI from the nats-box, which needs the decision 1 table to map it.
5. **cloud-provisioning PR 2**:
   - Set `preventDelete: false` on the CRs of the streams that go away: SALES_PHASE, NOTIFICATION, VENUE, TICKET_EMAIL, and the CR of `track-ticket-email`.
   - Remove the old KEDA triggers.
6. **cloud-provisioning PR 3**: remove those CRs. NACK then deletes the streams with their durables.
7. **By hand, once**: on each stream that stays (ORDER, CONCERT, ARTIST, USER, ORGANIZER), delete with `nats consumer rm` from the nats-box each durable that `nats consumer ls` lists but decision 1 does not place on that stream. These are the durables left behind by a move or a rename, such as `send-event-cancelled` on CONCERT and `track-user-logged-in` on USER. No CR refers to them, so NACK cannot remove them. This is the one-time action the tasks rule allows. Step 4 has confirmed each has 0 pending messages. A durable that decision 1 places on the stream is never deleted, whether it was moved there or kept there.

Why not new streams side by side with new CR names: a durable keeps its name, and the CR names would collide. Suffixing the new CRs would leave a permanent naming exception.

### 4. Docs and comments

The following are rewritten with the new names:
- The doc comment of every subject constant, which today also carries stale facts (SubjectOrderPaid names OrderUseCase.FulfillPayment, but Order.Issue announces it).
- `docs/event-delivery-design.md`, `docs/analytics/event-catalog.md` (its subject and event name columns), `docs/analytics/feature-flag-policy.md`, `docs/organizer-platform-design.md` and the proto comment.
- The comments in frontend `src/services/analytics-events.ts` that name backend analytics events.
- The analytics event constants in backend `internal/usecase/analytics_events.go` and the analytics consumer, which take the PostHog names of decision 1.
- The configmap comments that name `SALES_PHASE.discovered` and `SALES_PHASE.reminder.due` (a subject that does not exist).
- `cloud-provisioning/src/zitadel/constants.ts`, which names `USER.passkey_changed` (also nonexistent).

A grep for every old subject string and stream name across the four repositories must find nothing outside archived changes.

### 5. Agreement with add-flow-diagrams-to-specs

That change adds the events tables to the entity Purposes and draws the story diagrams. Its apply step named the events from the current prose. This change keeps the names it chose where the two agree, and adopts two of its choices:
- Artist.Represented: AssociateArtist makes the Artist represented by the Organizer.
- Organizer.Activated: CompareAndSetStatus records activation, and Organizer.Create is a separate operation.

This change then differs from its tables in two ways:
- It splits LotteryEntry.Drawn and ResaleEntry.Changed (decision 2). TicketJourney.StatusChanged keeps its name.
- It makes SeriesImage.Create announce SeriesImage.Uploaded, which that change left unlisted because no requirement announced it.

When this change archives, the entity events tables and the story diagrams that name the old events are edited directly in the main specs (Purpose), and `scripts/check-diagrams.py` must pass. If add-flow-diagrams-to-specs has not merged its Purpose edits by then, this change waits for it, so that the tables are edited once.

## Risks / Trade-offs

- [A message published to an old subject during the rollout is not consumed] → Steps 2 and 4 check the outbox and every old durable's pending count, and step 4 republishes any message left. With no users the expected count is 0.
- [NACK's behavior is read from the v0.25.0 source while 0.24.0 runs] → After PR 1 syncs, confirm with `nats consumer ls` on each new stream that the durables exist before the backend rollout. If a durable is missing, stop before step 3.
- [Renamed PostHog events start a new history; insights or actions created in PostHog by hand that name an old event stop matching] → The product has no users yet, so there is little history to lose. Task 2.6 lists the insights, actions and cohorts that name an old event and updates them.
- [The dev overlays cannot be verified while dev is stopped] → They are changed with the base manifests and kept coherent. Prod read-only checks are the verification.

## Migration Plan

Decision 3 is the plan. Rollback before step 5: revert the backend PR. The old durables still exist, so the previous version binds them again. After step 6, rollback means re-adding the removed streams.
