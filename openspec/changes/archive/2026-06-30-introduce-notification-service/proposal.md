## Why

Push notifications are **fire-and-forget**. The `2026-02-22-push-notification-new-concerts` change deliberately dropped the notification entity for the MVP and replaced it with a minimal `PushSubscription`, recording at the time that a notification-log table is "required for post-MVP features (delivery tracking, retry, in-app inbox)." That post-MVP moment has arrived, driven by two concrete product needs:

- **Delivery audit / reliability.** A production incident saw sales-reminder pushes silently deliver *nothing for weeks* (NATS_URL missing → goChannel void; consumer scale-to-zero deleting durables; webpush TTL=0 dropping for offline devices). With no per-notification delivery record there was nothing to observe — the failure was invisible until manually noticed. A notification log with per-channel delivery state makes "did this actually reach the user?" answerable and alertable.
- **In-app notification inbox / next-action surface.** Fans need to see what happened (and what to do next) without relying on a transient OS notification they may have missed. An inbox requires durable, per-user, read/unread notification records.

Because notifications are currently identity-less and stateless, three deferred analytics events from the archived `introduce-analytics-tool` change (Decision 14) also have no home: `notification.delivered` (task 13.2) and `notification.opened` / `notification.dismissed` (task 5.7). Those need a stable `notification_id` and a delivery/read lifecycle — exactly what this entity provides. They are **by-products**, not the driver: this change is justified by the inbox + delivery-audit product requirements on their own.

## What Changes

- Introduce a **notification** as a first-class persisted entity (a notification log): `id`, `user_id`, `type`, `payload`, `created_at`, plus per-channel delivery state and per-user read/dismiss state.
- Add an **outbox/dispatcher**: producing a notification creates one logical record, then fans it out to channels (web push now; email / in-app later) and records each channel's outcome (`queued → delivered`, or `failed`).
- Route the **existing producers** (`NotifyNewConcerts`, sales-reminder delivery) through the notification service instead of sending push directly, so every user-facing notification gets a durable record.
- Expose **read / dismiss** state transitions (mark-read, mark-dismissed) keyed by `notification_id`.
- This unblocks (as future follow-ups, not in this change) the deferred analytics lifecycle events and an in-app inbox UI: `delivered` = a channel send succeeded; `opened` / `dismissed` = the service-worker `notificationclick` / `close` handler correlating against the stable `notification_id`.

## Capabilities

### New Capabilities
- `notification-lifecycle`: notifications are durable, identified entities with a per-channel delivery lifecycle and a per-user read/dismiss state, dispatched via an outbox; all user-facing notifications flow through this service.

### Modified Capabilities
<!-- No existing capability spec's requirements change here; the existing push delivery is re-platformed onto the new entity but its observable behaviour (a fan receives a web push for new concerts / sales reminders) is preserved. -->

## Impact

- **backend** (primary): new `notifications` table + repository (Atlas migration under `k8s/atlas/base/migrations/`, schema in `rdb/schema/schema.sql`); a `NotificationUseCase` (entity-layer interface) that creates a record and dispatches via an outbox to the existing `entity.PushNotificationSender`; per-channel delivery-state recording; read/dismiss operations; rewire `push_notification_uc.NotifyNewConcerts` and `sales_reminder_delivery_uc.DeliverReminder` to go through it.
- **Out of scope (separate follow-ups):** the analytics event *emission* (`notification.delivered` / `.opened` / `.dismissed` — lands once the entity exists, re-opening `introduce-analytics-tool` tasks 13.2 / 5.7); the in-app **inbox UI** (frontend); any new inbox **RPC/proto** surface (noted as a follow-up — this change keeps the proto/API delta minimal and may expose read/dismiss via existing or one small RPC).
- **Risk/cost:** adds a write per notification on the delivery path (was fire-and-forget); mitigated by keeping the record write non-blocking to the send where appropriate and indexing on `(user_id, created_at)`.
