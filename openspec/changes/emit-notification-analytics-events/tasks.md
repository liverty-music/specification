## 1. Backend — `notification.delivered` emission

- [ ] 1.1 Add `SubjectNotificationDelivered = "NOTIFICATION.delivered"` and a `NotificationDeliveredData{ UserID, NotificationID, Type string }` (`json` tags) to `internal/entity/event_data.go`; ensure `EventNotificationDelivered` exists in `internal/usecase/analytics_events.go` and is in the `knownBackendEvents` allowlist.
- [ ] 1.2 Add `HandleNotificationDelivered` to `internal/adapter/event/analytics_consumer.go` mirroring `HandleNotificationSubscribed`: parse the CloudEvent, skip (non-fatal) on nil client / empty `user_id` / empty `notification_id`, build `AnalyticsProperties{ "notification_id": …, "type": … }`, and `Enqueue(ctx, UserID, EventNotificationDelivered, props)`. Unit-test the forward + skip paths.
- [ ] 1.3 Subscribe it in `internal/di/consumer.go`: `router.AddConsumerHandler("forward-notification-delivered-to-analytics", entity.SubjectNotificationDelivered, subscriber, analyticsConsumer.HandleNotificationDelivered)`. Confirm the existing `NOTIFICATION` JetStream stream already covers `NOTIFICATION.*` (no new stream) — see `internal/infrastructure/messaging/streams.go`.
- [ ] 1.4 Emit non-fatally from `NotificationUseCase` at the delivered transition (in `Notify`/`dispatch`, when the recorded status is `delivered`), exactly once per notification: `PublishEvent(ctx, SubjectNotificationDelivered, NotificationDeliveredData{UserID, NotificationID: n.ID, Type: string(typ)})`; log-and-continue on error. Unit-test: delivered ⇒ one emit; failed / no-subscription ⇒ no emit; publish error ⇒ non-fatal (delivery result unchanged).

## 2. Frontend — `notification.opened` / `.dismissed` emission

- [ ] 2.1 In the service-worker `push` handler (`src/sw.ts`), carry `notification_id` from the payload `data` into `showNotification` `options.data` (alongside `url`), so the interaction handlers can read it.
- [ ] 2.2 In `notificationclick`, after the existing navigation, stash a `notification.opened` interaction keyed by `data.notification_id` (skip when absent).
- [ ] 2.3 Add a `notificationclose` handler that stashes a `notification.dismissed` interaction keyed by `data.notification_id`.
- [ ] 2.4 Implement the SW interaction store: a small IndexedDB store of `{ event, notification_id, occurred_at }`, bounded (cap + drop-oldest) so it cannot grow unbounded when the PWA is not reopened.
- [ ] 2.5 In `AnalyticsService`, drain + flush the store on init: `capture` each interaction with an explicit event `timestamp = occurred_at`, delete the record only on successful enqueue, and honor opt-out (opted-out ⇒ drop without capture). Reuse the existing `NotificationOpenedProps` / `NotificationDismissedProps` typings in `src/services/analytics-events.ts`.
- [ ] 2.6 Tests: SW handlers stash the right event+id; `AnalyticsService` flush captures with the correct timestamp, dedups, and no-ops under opt-out.

## 3. Verification

- [ ] 3.1 Backend `make check` passes (lint + unit + integration).
- [ ] 3.2 Frontend `make check` passes (lint + unit + typecheck).
- [ ] 3.3 End-to-end: a delivered notification produces one `notification.delivered` in PostHog keyed by `notification_id`; clicking and dismissing a notification produce `notification.opened` / `notification.dismissed` after the next app open, correlated by the same `notification_id`.

## 4. Ship to production

- [ ] 4.1 Backend release → prod (server + consumer); confirm `notification.delivered` appears in PostHog for a real delivered notification. (No new NATS stream, so no consumer-crashloop risk.)
- [ ] 4.2 Frontend release → prod; confirm `notification.opened` / `notification.dismissed` land after a real interaction + app reopen.

## 5. Bookkeeping

- [ ] 5.1 This change satisfies the previously-descoped `introduce-analytics-tool` tasks 13.2 (`notification.delivered`) and 5.7 (`notification.opened` / `.dismissed`); note their completion. Closes #675.
- [ ] 5.2 Event catalogue already lists all three events — verify `specification/docs/analytics/event-catalog.md` still matches the emitted names/properties; update only if drift is found.
