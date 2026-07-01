## Why

`introduce-notification-service` shipped the notification log + a stable `notification_id` + a `queued → delivered/failed` lifecycle, but explicitly deferred analytics emission (its design Decision 5) and re-opened `introduce-analytics-tool` tasks 13.2 / 5.7 (Decision 14). Those events were descoped only because a `notification_id` and per-notification delivery/read state did not exist — both now do. The event catalogue already defines all three (`notification.delivered`, `.opened`, `.dismissed`); this change finally emits them, so "did notifications reach users?" (reach), "were they acted on?" (CTR), and "are we over-notifying?" (fatigue) become measurable — closing the loop on the delivery-audit motivation that drove the notification entity.

## What Changes

- **Backend — `notification.delivered`:** when a notification's channel send reaches `delivered`, the notification service publishes a `NOTIFICATION.delivered` domain event carrying the `notification_id` (+ `user_id`, `type`); the existing analytics-consumer forwards it to PostHog. Reuses the existing `NOTIFICATION.*` JetStream stream (no new stream) and the established non-fatal publish → consumer → `Enqueue` pattern.
- **Frontend — `notification.opened` / `.dismissed`:** the service worker's `push` handler carries `notification_id` (consolidated under the payload `data` alongside `url`) into the shown notification; the `notificationclick` / `notificationclose` handlers report the interaction **at interaction time** via `event.waitUntil(fetch(...))` to PostHog's `/capture` endpoint (a service worker cannot call `posthog-js`), honoring opt-out via a small client-synced `{ distinct_id, opted_out }` snapshot, with Background Sync / a bounded stash as an offline fallback only.
- **No proto, no DB migration, no new NATS stream.** The event catalogue already lists all three events; this is emission wiring only (plus a small backend `NotificationPayload` reshape to group client passthrough metadata under `data`).

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `notification-lifecycle`: adds the requirement that delivered/opened/dismissed transitions are reported to product analytics, correlated by `notification_id` (the analytics seam its Decision 5 deferred).

## Impact

- **backend:** new `NOTIFICATION.delivered` subject + `NotificationDeliveredData`; `analytics_consumer` handler + `di/consumer.go` subscription; a non-fatal emit at the `delivered` transition in `NotificationUseCase`. Reuses the existing NOTIFICATION stream — no crashloop risk from a missing stream.
- **frontend + backend payload reshape:** consolidate client passthrough metadata under the push payload `data` (`url` joins `notification_id`), leaving `title`/`body`/`tag` top-level; the SW `push` handler maps `data` into `showNotification` `options.data`; new `notificationclick` capture + `notificationclose` handler send via `event.waitUntil(fetch(...))` to PostHog `/capture`, gated by a client-synced opt-out/identity snapshot, with Background Sync / bounded-stash offline fallback. The backend `NotificationPayload` struct moves `URL` into its `Data` map.
- **out of scope:** enriching events with optional `event_id` / `artist_id` (catalogue marks them optional); the in-app inbox (#676); the `notification_deliveries` child table (#677).
