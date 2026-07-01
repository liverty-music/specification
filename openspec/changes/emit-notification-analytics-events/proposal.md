## Why

`introduce-notification-service` shipped the notification log + a stable `notification_id` + a `queued → delivered/failed` lifecycle, but explicitly deferred analytics emission (its design Decision 5) and re-opened `introduce-analytics-tool` tasks 13.2 / 5.7 (Decision 14). Those events were descoped only because a `notification_id` and per-notification delivery/read state did not exist — both now do. The event catalogue already defines all three (`notification.delivered`, `.opened`, `.dismissed`); this change finally emits them, so "did notifications reach users?" (reach), "were they acted on?" (CTR), and "are we over-notifying?" (fatigue) become measurable — closing the loop on the delivery-audit motivation that drove the notification entity.

## What Changes

- **Backend — `notification.delivered`:** when a notification's channel send reaches `delivered`, the notification service publishes a `NOTIFICATION.delivered` domain event carrying the `notification_id` (+ `user_id`, `type`); the existing analytics-consumer forwards it to PostHog. Reuses the existing `NOTIFICATION.*` JetStream stream (no new stream) and the established non-fatal publish → consumer → `Enqueue` pattern.
- **Frontend — `notification.opened` / `.dismissed`:** the service worker's `push` handler carries `notification_id` from the payload `data` into the shown notification; the `notificationclick` / `notificationclose` handlers record the interaction keyed by that id and bridge it to the app's `AnalyticsService` (a service worker cannot call `posthog-js` directly).
- **No proto, no DB migration, no new NATS stream.** The event catalogue already lists all three events; this is emission wiring only.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `notification-lifecycle`: adds the requirement that delivered/opened/dismissed transitions are reported to product analytics, correlated by `notification_id` (the analytics seam its Decision 5 deferred).

## Impact

- **backend:** new `NOTIFICATION.delivered` subject + `NotificationDeliveredData`; `analytics_consumer` handler + `di/consumer.go` subscription; a non-fatal emit at the `delivered` transition in `NotificationUseCase`. Reuses the existing NOTIFICATION stream — no crashloop risk from a missing stream.
- **frontend:** SW `push` handler propagates `notification_id` into `showNotification` `data`; new `notificationclick` interaction capture + `notificationclose` handler; a SW→app analytics bridge (stash + flush-on-load) so opt-out and `trace_id` still flow through `AnalyticsService`.
- **out of scope:** enriching events with optional `event_id` / `artist_id` (catalogue marks them optional); the in-app inbox (#676); the `notification_deliveries` child table (#677).
