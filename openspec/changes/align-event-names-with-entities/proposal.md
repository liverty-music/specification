## Why

The same domain event has a different name in each place that refers to it. Consider the event for a cancelled Event:
- The spec says "announce that Event as cancelled".
- The Go constant is `SubjectConcertCancelled`.
- The NATS subject is `CONCERT.cancelled`, in the CONCERT stream.

Other cases:
- Lottery and resale events live in the ORDER stream (`ORDER.lottery_entry_drawn`).
- TicketSale events use the retired name SALES_PHASE.
- Follow events are named after the Artist (`ARTIST.followed`).
- PushSubscription events are named after notifications (`NOTIFICATION.subscribed`).

Two events cover several outcomes that their consumers react to differently, so each consumer reads the payload and drops what it does not act on:
- `ORDER.resale_entry_changed` covers Won, Lapsed, Lost and Withdrawn.
- `ORDER.lottery_entry_drawn` covers Won and Lost, and is also announced when a win is reverted or an entry is ended.

The PostHog events forwarded from domain events have names of their own again (`ticket.lottery.result`, `artist.follow.completed`, `account.signin`).

The change add-flow-diagrams-to-specs makes events part of the spec vocabulary (`<Entity>.<PastTense>`). This change makes code, infrastructure and docs use the same names, so a reader can follow one name from a spec to a subject, a stream and a consumer.

## What Changes

- **Spec**: every requirement that announces an event names it, as in "announce the entry as won (LotteryEntry.Won)". 34 entity operation specs and one usecase spec are modified. The event names are:
  - Concert.Created, Event.Cancelled, Artist.Created
  - Follow.Created, Follow.Removed, Follow.HypeChanged
  - User.Created, User.SignedIn, Passkey.Added, Passkey.Removed
  - PushSubscription.Subscribed, PushSubscription.Unsubscribed
  - TicketSale.Discovered
  - TicketJourney.StatusChanged
  - Organizer.Activated, Artist.Represented, SeriesImage.Uploaded
  - Order.Paid, Order.Refunded, ResaleListing.Sold, ResaleListing.Refunded
  - LotteryEntry.Entered, LotteryEntry.Won, LotteryEntry.Lost
  - ResaleEntry.Won, ResaleEntry.Lapsed, ResaleEntry.Lost, ResaleEntry.Withdrawn
  - Checkout.Held, Checkout.Expired, Checkout.Released, Ticket.Admitted
- **Split events**: an event is split by state only where consumers react to the states differently. Each consumer then subscribes only to the states it acts on:
  - `ORDER.resale_entry_changed` becomes four events.
  - `ORDER.lottery_entry_drawn` becomes LotteryEntry.Won and LotteryEntry.Lost.
  - TicketJourney.StatusChanged stays one event, since its only consumer treats every status the same.
- **PostHog**: an analytics event forwarded from a domain event is named by its subject in lower case (`lottery_entry.won`, `follow.created`, `user.signed_in`). `user.created`, `order.paid`, `checkout.expired` and `ticket.admitted` keep their names.
- **Subjects and streams (BREAKING for the event pipeline)**:
  - Every subject becomes `<ENTITY>.<event>` (`LOTTERY_ENTRY.won`), and each entity's events live in a stream named after the entity.
  - New streams: EVENT, FOLLOW, PASSKEY, PUSH_SUBSCRIPTION, TICKET_SALE, LOTTERY_ENTRY, RESALE_ENTRY, RESALE_LISTING, CHECKOUT and TICKET.
  - Removed streams: SALES_PHASE, NOTIFICATION, and the unused VENUE and TICKET_EMAIL streams.
  - Durables whose names carry a retired name are renamed (`notify-sales-phase` becomes `notify-ticket-sale-discovered`), and the unused durable `track-ticket-email` is removed.
- **Go**: the subject constants, the stream registry, the behavior table, the consumer files and the doc comments use the event names.
- **Infrastructure**: the NACK Stream and Consumer manifests and the KEDA triggers in cloud-provisioning follow the new streams and durables. The durables and streams that are no longer used are removed from production.
- **Docs**: specification `docs/event-delivery-design.md` and `docs/analytics/event-catalog.md`, a proto comment, and the configmap comments use the new subjects.
- **Entity events tables and story diagrams**: add-flow-diagrams-to-specs lists the events in each entity's Purpose and draws them in the story diagrams. The tables and diagrams that name a split event, and the SeriesImage table, are updated to the names above.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/entity/artist/create`: the announcement names Artist.Created.
- `components/entity/checkout/get-or-create-held`, `components/entity/checkout/release`, `components/entity/checkout/revert-commit`: the announcements name Checkout.Held, Checkout.Expired and Checkout.Released.
- `components/entity/concert/create`, `components/entity/series/publish-events`: the announcements name Concert.Created.
- `components/entity/series/cancel-events`: names Event.Cancelled.
- `components/entity/follow/follow`, `components/entity/follow/unfollow`, `components/entity/follow/set-hype`, `components/entity/follow/raise-hype`: the announcements name Follow.Created, Follow.Removed and Follow.HypeChanged.
- `components/entity/lottery-entry/create`, `components/entity/lottery-entry/persist-draw-outcome`, `components/entity/lottery-entry/revert-win`, `components/entity/lottery-entry/end-entered-by-event`: the announcements name LotteryEntry.Entered, LotteryEntry.Won and LotteryEntry.Lost. The draw announces Won and Lost entries as separate events.
- `components/entity/resale-entry/persist-draw-outcome`, `components/entity/resale-entry/revert-win`, `components/entity/resale-entry/withdraw`: the announcements name ResaleEntry.Won, ResaleEntry.Lapsed, ResaleEntry.Lost and ResaleEntry.Withdrawn, one event per state.
- `components/entity/resale-listing/record-refund`: names ResaleListing.Refunded.
- `components/entity/order/issue`, `components/entity/order/commit-refund`: the announcements name Order.Paid, ResaleListing.Sold and Order.Refunded.
- `components/entity/organizer/associate-artist`, `components/entity/organizer/compare-and-set-status`: the announcements name Artist.Represented and Organizer.Activated.
- `components/entity/passkey/create`, `components/entity/passkey/delete`: the announcements name Passkey.Added and Passkey.Removed.
- `components/entity/push-subscription/create`, `components/entity/push-subscription/delete`: the announcements name PushSubscription.Subscribed and PushSubscription.Unsubscribed.
- `components/entity/series-image/create`: the processing request is announced as SeriesImage.Uploaded.
- `components/entity/ticket/admit`: names Ticket.Admitted.
- `components/entity/ticket-journey/upsert`, `components/entity/ticket-journey/upsert-if-replaceable`: the announcement names TicketJourney.StatusChanged.
- `components/entity/ticket-sale/upsert-discovered`: names TicketSale.Discovered.
- `components/entity/user/create`, `components/entity/user/record-login`: the announcements name User.Created and User.SignedIn.
- `components/usecase/ticket-journey/mark-applied`: runs for LotteryEntry.Entered.

Purpose edits, made directly in the main specs when this change archives: the events tables of LotteryEntry, ResaleEntry and SeriesImage (Purpose), and every story diagram that draws a split event (Purpose). No usecase other than MarkApplied changes: the usecases that run from an event already describe it by the state it announces ("each LotteryEntry announced Lost").

## Impact

- **backend**:
  - `internal/entity/event_data.go`, `internal/infrastructure/messaging/streams.go` and its test data
  - the announcing repositories under `internal/infrastructure/database/rdb/`
  - the consumers under `internal/adapter/event/`
  - `internal/di/consumer.go`
  - the tests that name subjects
- **cloud-provisioning**:
  - `k8s/namespaces/nats/base/jetstream/` (Stream and Consumer manifests)
  - `k8s/namespaces/backend/base/event-consumer/scaledobject.yaml` (KEDA)
  - configmap comments
  - production: a one-time removal of the durables that the stream moves leave behind
- **specification**:
  - `docs/event-delivery-design.md`
  - `docs/analytics/event-catalog.md`
  - the comment in `proto/liverty_music/rpc/organizer/series/v1/series_service.proto`
- **frontend**: comments in `src/services/analytics-events.ts` that name backend analytics events.
- **PostHog**: the renamed events start a new history; insights, actions or cohorts that name an old event are updated.
