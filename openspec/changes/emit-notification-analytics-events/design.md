## Context

The notification-lifecycle capability now persists each notification with a stable `notification_id`, transitions it `queued → delivered/failed`, and carries the id into the web-push payload `data.notification_id`. The product-analytics capability already defines a NATS→`analytics-consumer`→PostHog backend flow and a deferred-init `posthog-js` frontend flow, and the event catalogue already lists the three target events:

| Event | Source | Properties |
|---|---|---|
| `notification.delivered` | BE | `notification_id`, `event_id?`, `artist_id?`, `trace_id?` |
| `notification.opened` | FE | `notification_id`, `event_id?`, `artist_id?`, `trace_id?` |
| `notification.dismissed` | FE | `notification_id`, `trace_id?` |

Backend emission mirrors the live `notification.subscribed`/`.unsubscribed` path exactly (subject constant → `*Data` struct → `PublishEvent` → `analytics_consumer.Handle*` → `client.Enqueue`). The frontend piece is the hard part: a service worker has no `window`, so it cannot call `posthog-js` directly.

## Goals / Non-Goals

**Goals:**
- Emit `notification.delivered` (BE) exactly once when a notification's channel send reaches `delivered`, keyed by `notification_id`.
- Emit `notification.opened` / `notification.dismissed` (FE) from the service-worker `notificationclick` / `notificationclose` handlers, keyed by the `notification_id` carried in the notification payload.
- Route the frontend events through the app's `AnalyticsService` so opt-out and `trace_id` semantics are preserved.
- Reuse existing infrastructure — no new NATS stream, no proto, no DB migration.

**Non-Goals:**
- Enriching events with the optional `event_id` / `artist_id` (catalogue marks them `?`); deferred until a cheap source is threaded through the notification payload.
- A `notification.failed` analytics event — failures are already auditable in the `notifications` table; the catalogue intentionally has no failed event.
- Real-time delivery of `opened`/`dismissed` (see Decision 3 — they are flushed on next app open).
- The in-app inbox (#676) and `notification_deliveries` child table (#677).

## Decisions

### Decision 1: Emit `notification.delivered` once, generically, at the delivered transition
The notification service already computes a single terminal outcome per notification and calls `UpdateDelivery(...)` once. Emit `NOTIFICATION.delivered` at that point when (and only when) the status is `delivered`. Because every producer (new-concert, sales-reminder, sales-phase announcement) funnels through the one service, this single hook covers all of them and fires **once per notification**, not once per push subscription. Payload: `NotificationDeliveredData{ UserID, NotificationID, Type }`. Publish is **non-fatal** (log-and-continue), identical to the existing `notification.subscribed` emit — analytics must never affect delivery.

### Decision 2: Reuse the `NOTIFICATION` JetStream stream; add only a handler + subscription
`NOTIFICATION.delivered` matches the existing `NOTIFICATION.*` stream, so **no new stream is required** — this deliberately avoids the missing-stream consumer crashloop that blocked a prior release. The work is: a `SubjectNotificationDelivered` constant, a `HandleNotificationDelivered` in `analytics_consumer` (same shape as `HandleNotificationSubscribed`: parse → validate `user_id`/`notification_id` → `Enqueue`), and one `router.AddConsumerHandler(...)` line in `di/consumer.go`. Missing the DI line would silently drop the event, so it is an explicit task.

### Decision 3: SW→app analytics bridge = stash-and-flush, not a direct SW→PostHog call
A service worker cannot use `posthog-js`. Three options:

| Approach | click | close | opt-out / trace honored | latency |
|---|---|---|---|---|
| `postMessage` to a client | ok if a client is focused | ✗ (no client on close) | via app | low |
| SW `fetch` → PostHog `/capture` | ok | ok | ✗ (bypasses AnalyticsService) | low |
| **IndexedDB stash → flush on app load** | ok (click opens/focuses app) | ok (flushed next open) | ✓ (via AnalyticsService) | delayed |

Chosen: **stash-and-flush.** It is the only option that reliably captures *both* `notificationclick` (which may open a fresh client) *and* `notificationclose` (no client at all) while still routing through `AnalyticsService`, so opt-out and `trace_id` are respected. The SW writes `{ event, notification_id, occurred_at }` to a small IndexedDB store; on boot, `AnalyticsService` drains and `capture()`s each with an explicit event `timestamp = occurred_at` (so the interaction isn't misattributed to flush time), then deletes the drained record. If the user is opted out, `capture` no-ops and the record is dropped. `notificationclick` still `openWindow`/focuses as today; the added capture is orthogonal to navigation.

### Decision 4: Carry `notification_id` into the shown notification's `data`
The backend already includes `data.notification_id` in the push JSON. The SW `push` handler currently copies only `url` into `showNotification`'s `data` bag; extend it to also copy `notification_id` (and pass through `url`), so `notificationclick`/`close` — which only see `event.notification.data` — can read the id. No backend change needed; this is the FE half of the already-shipped "id propagated end-to-end" requirement.

## Risks / Trade-offs

- **[Trade-off] Delayed `opened`/`dismissed`** — flushed on next app open, not real-time. Acceptable for product analytics (funnel/fatigue), and the explicit `timestamp` preserves temporal accuracy. If the user never reopens the PWA after a dismiss, that event is lost — best-effort, with a bounded store (cap + drop-oldest) to avoid unbounded growth.
- **[Risk] Double counting on flush** — a record must be deleted only after a successful `capture` enqueue; the store is keyed so a re-flush of an already-sent record is a no-op. Mirrors the pre-init queue discipline already in `AnalyticsService`.
- **[Risk] `delivered` event volume** — one event per delivered notification can be high for popular artists (PostHog cost). This is the intended "reach" metric; volume is bounded by real notification volume and is the whole point of the audit. Revisit sampling only if cost warrants.
- **[Trade-off] No `event_id`/`artist_id`** — reduces slice-ability of reach/CTR by artist/event for now. The properties are catalogue-optional; adding them later is additive (thread the ids through `NotificationDeliveredData` and the payload `data`).
- **[Risk] distinct_id at interaction time** — a notification opened after logout attaches to the anonymous id; PostHog merges anon→identified on next `identify`, so the funnel still reconciles. No special handling needed.
