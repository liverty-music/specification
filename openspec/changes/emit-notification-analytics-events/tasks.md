## 1. Backend — `notification.delivered` emission

- [x] 1.1 Add `SubjectNotificationDelivered = "NOTIFICATION.delivered"` and a `NotificationDeliveredData{ UserID, NotificationID, Type string }` (`json` tags) to `internal/entity/event_data.go`; ensure `EventNotificationDelivered` exists in `internal/usecase/analytics_events.go` and is in the `knownBackendEvents` allowlist.
- [x] 1.2 Add `HandleNotificationDelivered` to `internal/adapter/event/analytics_consumer.go` mirroring `HandleNotificationSubscribed`: parse the CloudEvent, skip (non-fatal) on nil client / empty `user_id` / empty `notification_id`, build `AnalyticsProperties{ "notification_id": …, "type": … }`, and `Enqueue(ctx, UserID, EventNotificationDelivered, props)`. Unit-test the forward + skip paths.
- [x] 1.3 Subscribe it in `internal/di/consumer.go`: `router.AddConsumerHandler("forward-notification-delivered-to-analytics", entity.SubjectNotificationDelivered, subscriber, analyticsConsumer.HandleNotificationDelivered)`. Confirm the existing `NOTIFICATION` JetStream stream already covers `NOTIFICATION.*` (no new stream) — see `internal/infrastructure/messaging/streams.go`.
- [x] 1.4 Emit non-fatally from `NotificationUseCase` at the delivered transition (in `Notify`/`dispatch`, when the recorded status is `delivered`), exactly once per notification: `PublishEvent(ctx, SubjectNotificationDelivered, NotificationDeliveredData{UserID, NotificationID: n.ID, Type: string(typ)})`; log-and-continue on error. Unit-test: delivered ⇒ one emit; failed / no-subscription ⇒ no emit; publish error ⇒ non-fatal (delivery result unchanged).
- [x] 1.5 Reshape `entity.NotificationPayload` so client passthrough metadata lives under the `Data` map: move `URL` into `Data` (joining `notification_id`), keeping `Title`/`Body`/`Tag` top-level. Update the three producers that build payloads and any marshalling; the wire JSON becomes `{ title, body, tag, data: { url, notification_id } }`. Adjust existing backend tests.

## 2. Frontend — `notification.opened` / `.dismissed` emission

- [x] 2.1 In the service-worker `push` handler (`src/sw.ts`), map the payload `data` object straight into `showNotification` `options.data`, so `notificationclick`/`close` can read `event.notification.data.{ url, notification_id }`. During rollout, read `url`/`notification_id` from **both** the new nested `data` and the legacy top-level location (compat shim) so in-flight payloads still navigate.
- [x] 2.2 Maintain a service-worker-readable identity snapshot `{ distinct_id, opted_out }`: the app writes it (Cache/IndexedDB) on `identify` and on analytics opt-out change; the SW reads it when reporting interactions.
- [x] 2.3 In `notificationclick` (after the existing navigation) and a new `notificationclose` handler, report `notification.opened` / `notification.dismissed` via `event.waitUntil(fetch(POSTHOG_CAPTURE_URL, { method: 'POST', keepalive: true, body }))`, keyed by `data.notification_id` (skip when absent). The body carries `distinct_id`, `event`, `properties.notification_id`, an explicit `timestamp` = interaction time, and a per-interaction `uuid` (`$insert_id`) for dedup. **Skip the send entirely when the snapshot says `opted_out`.**
- [x] 2.4 Offline fallback: on `fetch` failure, retry via the Background Sync API where available (Chromium); otherwise write the interaction to a **bounded** IndexedDB stash (cap + drop-oldest) and flush it on next SW activation / app open. Reuse the same `uuid` so retries dedup.
- [x] 2.5 Reuse the existing `NotificationOpenedProps` / `NotificationDismissedProps` typings in `src/services/analytics-events.ts`; centralize the capture-body builder so it matches the app SDK's PostHog event shape (event name, `distinct_id`, `$insert_id`, `timestamp`).
- [x] 2.6 Tests: SW `push` maps `data`→`options.data` (with compat shim); click/close call `fetch` with the right event+`notification_id`+`timestamp`+`uuid`; opted-out snapshot ⇒ no `fetch`; `fetch`-failure path enqueues the bounded stash / Background Sync retry without duplicating.

## 3. Verification

- [x] 3.1 Backend `make check` passes (lint + unit + integration).
- [x] 3.2 Frontend `make check` passes (lint + unit + typecheck).
- [ ] 3.3 End-to-end: a delivered notification produces one `notification.delivered` in PostHog keyed by `notification_id`; clicking and dismissing a notification produce `notification.opened` / `notification.dismissed` **at interaction time** (offline: after reconnect via Background Sync / stash flush), correlated by the same `notification_id`; an opted-out user produces neither.

## 4. Ship to production

- [ ] 4.1 Backend release → prod (server + consumer); confirm `notification.delivered` appears in PostHog for a real delivered notification. (No new NATS stream, so no consumer-crashloop risk.)
- [ ] 4.2 Frontend release → prod; confirm `notification.opened` / `notification.dismissed` land after a real interaction + app reopen.

## 5. Bookkeeping

- [ ] 5.1 This change satisfies the previously-descoped `introduce-analytics-tool` tasks 13.2 (`notification.delivered`) and 5.7 (`notification.opened` / `.dismissed`); note their completion. Closes #675.
- [x] 5.2 Event catalogue already lists all three events — verify `specification/docs/analytics/event-catalog.md` still matches the emitted names/properties; update only if drift is found.
