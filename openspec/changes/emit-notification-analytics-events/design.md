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
- Emit `notification.opened` / `notification.dismissed` (FE) from the service-worker `notificationclick` / `notificationclose` handlers **at interaction time**, keyed by the `notification_id` carried in the notification.
- Honor the user's analytics opt-out for the frontend events even though the service worker cannot run `posthog-js`.
- Reuse existing infrastructure — no new NATS stream, no proto, no DB migration.

**Non-Goals:**
- Enriching events with the optional `event_id` / `artist_id` (catalogue marks them `?`); deferred until a cheap source is threaded through the notification payload.
- A `notification.failed` analytics event — failures are already auditable in the `notifications` table; the catalogue intentionally has no failed event.
- `trace_id` correlation on `opened` / `dismissed` — the service worker has no active OTel span, so these two events carry no `trace_id` (catalogue-optional); the backend `delivered` event keeps its `trace_id`.
- The in-app inbox (#676) and `notification_deliveries` child table (#677).

## Decisions

### Decision 1: Emit `notification.delivered` once, generically, at the delivered transition
The notification service already computes a single terminal outcome per notification and calls `UpdateDelivery(...)` once. Emit `NOTIFICATION.delivered` at that point when (and only when) the status is `delivered`. Because every producer (new-concert, sales-reminder, sales-phase announcement) funnels through the one service, this single hook covers all of them and fires **once per notification**, not once per push subscription. Payload: `NotificationDeliveredData{ UserID, NotificationID, Type }`. Publish is **non-fatal** (log-and-continue), identical to the existing `notification.subscribed` emit — analytics must never affect delivery.

### Decision 2: Reuse the `NOTIFICATION` JetStream stream; add only a handler + subscription
`NOTIFICATION.delivered` matches the existing `NOTIFICATION.*` stream, so **no new stream is required** — this deliberately avoids the missing-stream consumer crashloop that blocked a prior release. The work is: a `SubjectNotificationDelivered` constant, a `HandleNotificationDelivered` in `analytics_consumer` (same shape as `HandleNotificationSubscribed`: parse → validate `user_id`/`notification_id` → `Enqueue`), and one `router.AddConsumerHandler(...)` line in `di/consumer.go`. Missing the DI line would silently drop the event, so it is an explicit task.

### Decision 3: Report `opened`/`dismissed` at interaction time via `event.waitUntil(fetch(...))`, with a stash only as an offline fallback
A service worker cannot use `posthog-js` (no `window`). But `notificationclick` / `notificationclose` are *extendable events*, so the platform-canonical way to report them is `event.waitUntil(fetch(...))`: the browser keeps the worker alive until the request settles, and it works even when **no client/window is open** — which is always the case for `notificationclose`. This is strictly more reliable and immediate than the alternatives:

| Approach | click | close (no client) | opt-out / identity honored | latency / loss |
|---|---|---|---|---|
| `postMessage` to a client | ok if focused | ✗ no client on close | via app | — |
| IndexedDB stash → flush on next app open | ok | ok | ✓ via `AnalyticsService` | ✗ delayed; lost if never reopened |
| `fetchLater()` | window-only | ✗ | — | not available in a service worker |
| **`event.waitUntil(fetch(...))`** | ✅ | ✅ | ✅ via a client-synced snapshot | immediate |

Chosen: **`event.waitUntil(fetch(...))` from the handlers.** Each handler sends one PostHog `capture` (`event`, `distinct_id`, `properties.notification_id`, explicit `timestamp` = interaction time, and a per-interaction `uuid` for dedup) via `fetch(POSTHOG_CAPTURE_URL, { method: 'POST', keepalive: true, body })`. Targeting PostHog's public `/capture` HTTP endpoint directly keeps the events **frontend-sourced** and needs no new backend surface (the project key is already a public client value).

Because the worker has no `posthog-js` and does not know the signed-in user, the app writes a tiny **identity snapshot** `{ distinct_id, opted_out }` to a service-worker-readable store (Cache/IndexedDB) and refreshes it on `identify` / opt-out change. The handler reads the snapshot, **skips the send entirely when `opted_out`**, and stamps `distinct_id`. `notificationclick` still `openWindow`/focuses as today — the capture is orthogonal to navigation.

**Offline fallback:** a `fetch` that fails (offline at click/close) is retried via the **Background Sync API** where available (Chromium); on browsers without it (Safari/Firefox) the interaction is written to a small **bounded** IndexedDB stash and flushed on the next service-worker activation / app open. The stash is thus demoted from the primary mechanism to a best-effort offline fallback, not the happy path.

### Decision 4: Consolidate client passthrough metadata under the payload `data`
`NotificationOptions.data` is the only channel through which `notificationclick`/`close` can read per-notification metadata, so `notification_id` must live there. Today the wire payload is inconsistent: `url` (client passthrough, used by click navigation) sits **top-level** while `notification_id` sits under `data`. Consolidate all client-passthrough metadata under one `data` object — `data: { url, notification_id, … }` — leaving only the native notification fields (`title`, `body`, `tag`) at the top level. The SW maps `payload.data` straight into `showNotification`'s `options.data`, so `notificationclick`/`close` read `event.notification.data.{ url, notification_id }` uniformly, and future `event_id`/`artist_id` slot in additively.

This touches the backend `NotificationPayload` shape (move `URL` into the `data` map alongside `notification_id`) and the SW `push` handler together — a coordinated backend + frontend change. During rollout the SW SHOULD read `url`/`notification_id` from **both** the new nested `data` and the legacy top-level location, so an in-flight old payload (or an old SW against a new payload) still navigates; the compat shim is removed once both sides are deployed.

## Risks / Trade-offs

- **[Trade-off] Offline loss on non-Background-Sync browsers** — the `waitUntil(fetch)` sends at interaction time, so the delayed/lost window is now only the *offline* case. Where Background Sync exists (Chromium) the send is retried automatically; on Safari/Firefox the bounded stash flushes on next app open, and an interaction whose device never reconnects-then-reopens is lost. Best-effort, and a far smaller loss surface than a stash-always design.
- **[Risk] Retry double-counting** — a Background-Sync / stash retry could resend an interaction. Each capture carries a stable per-interaction `uuid` (PostHog `$insert_id`) so a resend is de-duplicated server-side; the stash entry is deleted only after a successful send.
- **[Risk] Direct SW→PostHog coupling** — the worker posts to PostHog's public `/capture` endpoint with the public project key. Only non-PII properties (`notification_id`) and the `distinct_id` are sent; no secret is exposed (the same key already ships in the web client). If PostHog's ingestion contract changes, the SW path must be updated alongside the app SDK.
- **[Risk] `delivered` event volume** — one event per delivered notification can be high for popular artists (PostHog cost). This is the intended "reach" metric; volume is bounded by real notification volume and is the whole point of the audit. Revisit sampling only if cost warrants.
- **[Risk] `delivered` double-count on consumer redelivery** — `delivered` fires once per notification *record*; an at-least-once redelivery of the producer event (e.g. `CONCERT.discovered`) creates a new record with a new `notification_id` and thus a second `delivered`. Rare (handler-retry only) and already a property of the notification log; treated as acceptable inflation of the reach count, not corrected here.
- **[Trade-off] Backend `delivered` does not consult client opt-out** — like the existing `sales_reminder.delivered`, the server-side `delivered` event is emitted regardless of the recipient's client-side analytics opt-out (opt-out is enforced client-side and is not persisted server-side). The FE `opened`/`dismissed` events **do** honor opt-out via the identity snapshot. This asymmetry is deliberate and consistent with the existing backend analytics events.
- **[Trade-off] No `event_id`/`artist_id`** — reduces slice-ability of reach/CTR by artist/event for now. The properties are catalogue-optional; adding them later is additive (thread the ids through `NotificationDeliveredData` and the payload `data`).
- **[Risk] Identity snapshot staleness** — `distinct_id`/`opted_out` reflect the app's last-synced snapshot, so there is a brief window right after login/logout/opt-out-toggle before the SW sees the new value. Interactions in that window may attribute to the prior identity; PostHog's anon→identified merge reconciles aggregate funnels. Refresh the snapshot on `identify` and opt-out change to keep the window small.
