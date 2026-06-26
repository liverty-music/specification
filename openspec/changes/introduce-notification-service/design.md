## Context

Notifications today are sent directly from use cases (`push_notification_uc.NotifyNewConcerts`, `sales_reminder_delivery_uc.DeliverReminder`) to `entity.PushNotificationSender` (web push) with no persistence. `NotificationPayload` carries `Title/Body/URL/Tag` and is discarded after the send. The `2026-02-22-push-notification-new-concerts` design explicitly chose this fire-and-forget posture for the MVP and documented the post-MVP entity as the unlock for delivery tracking, retry, and an in-app inbox.

The backend is Go / Clean Architecture (entity interfaces, usecase business logic, infrastructure adapters, manual DI), pgx/pgxpool for PostgreSQL, Atlas for migrations (operator-applied in prod; `make test` applies locally), CloudEvents over NATS for async work. The same outbox-style "record then dispatch, record outcome" shape already exists for analytics forwarding (publish → consumer → enqueue) and for sales-reminder delivery.

## Goals / Non-Goals

**Goals:**
- A notification is a durable, identified entity (`notification_id`) with a per-channel delivery lifecycle (`queued → sent → delivered → failed`) and a per-user read/dismiss state.
- Every user-facing notification (new-concert pushes, sales reminders) flows through one notification service, so each produces a record and a delivery outcome.
- "Did this notification reach the user?" is queryable and alertable (delivery audit), addressing the silent-delivery-failure incident.
- Read/dismiss can be set against a stable `notification_id`.
- The entity is structured so the deferred analytics events (`notification.delivered` / `.opened` / `.dismissed`) and an in-app inbox can be built on top **without re-modelling** — those are explicit follow-ups, not this change.

**Non-Goals:**
- Emitting the analytics events themselves (re-opens `introduce-analytics-tool` 13.2 / 5.7 once this lands).
- The in-app inbox **UI** (separate frontend change).
- Email / SMS channels (the dispatcher is channel-extensible, but only web push is wired now).
- A general workflow/retry engine — retry here is bounded (re-dispatch a `failed` channel), not a saga framework.

## Decisions

### Decision 1: A `notifications` log table, channel-state on the same row (single-channel now)

Persist one row per logical notification: `id (uuid)`, `user_id`, `type` (enum: `new_concerts`, `sales_reminder`, …), `payload (jsonb)`, `created_at`, and — because web push is the only channel today — the channel delivery state inline (`delivery_status`: `queued|sent|delivered|failed`, `delivered_at`, `failure_reason`) plus read state (`read_at`, `dismissed_at`). A separate `notification_deliveries` table (one row per channel) is the clean multi-channel shape, but is deferred: with one channel it is premature normalization. The migration is written so a later split to a child table is additive. Indexed on `(user_id, created_at desc)` for inbox queries.

### Decision 2: Outbox dispatch — create the record first, then send, then record the outcome

`NotificationUseCase.Notify(ctx, userID, type, payload)` (1) inserts the `queued` record, (2) dispatches to the channel via the existing `PushNotificationSender`, (3) updates the row to `delivered`/`failed` with the result already in hand. The record write is the source of truth; a send failure marks `failed` (and is re-dispatchable) rather than losing the notification. This mirrors the existing sales-reminder "record-sent then send" ordering and keeps the delivery path observable. The DB write is on the critical path (unlike today's fire-and-forget) — accepted for auditability; kept to a single indexed insert + one update.

### Decision 3: Producers call the service, not the sender

`NotifyNewConcerts` and `DeliverReminder` switch from calling `PushNotificationSender.Send` directly to calling `NotificationUseCase.Notify`. Their existing once-only / audience-resolution logic stays; only the final send is replaced. This is the seam that gives every user-facing notification a record without changing what users receive.

### Decision 4: Read/dismiss are explicit state transitions keyed by `notification_id`

`MarkRead(ctx, userID, notificationID)` and `MarkDismissed(...)` set `read_at`/`dismissed_at` (idempotent, user-scoped). These are the hooks an inbox and the future `notification.opened`/`dismissed` analytics events call. Exposure (RPC vs reuse) is kept minimal in this change; if an inbox RPC is needed it is called out as a follow-up rather than designed here.

### Decision 5: Analytics emission is a documented seam, not built here

The entity is shaped so that, in a later change, `notification.delivered` is emitted when a channel reaches `delivered`, and `notification.opened`/`dismissed` are emitted from the service-worker `notificationclick`/`close` handler correlating the OS notification's `tag`/`data.notification_id` back to the record. This change only guarantees the `notification_id` exists end-to-end (record → push payload `data.notification_id` → SW), so the future emission has a stable key.

## Risks / Trade-offs

- **[Risk] Added write on the delivery path** (was fire-and-forget) → a DB hiccup could now affect sends. Mitigation: a single indexed insert + one update. **On record-write failure the send is NOT performed blind** — the operation fails and surfaces the error so the producer's existing retry / at-least-once path re-drives it. This is deliberate and consistent with the spec's "record is the source of truth": an *unobservable* send is exactly the silent-delivery bug this change exists to eliminate, so we never send something we couldn't record. (An earlier draft proposed a best-effort send-without-record fallback — rejected, because it re-creates the unobservable hole in the DB-down case.) Revisit async-record only if the synchronous insert shows latency, keeping the "no record ⇒ no send" invariant.
- **[Risk] Backfill / dual-write window** while producers migrate → migrate `NotifyNewConcerts` and `DeliverReminder` together in this change; no notification source bypasses the service after it lands.
- **[Trade-off] Inline channel-state vs `notification_deliveries` child table** → chose inline for the single web-push channel; documented as additively splittable when email/in-app arrive. Avoids premature normalization.
- **[Trade-off] Scope discipline** → analytics emission and inbox UI are explicitly deferred so this change ships the capability (entity + dispatch + read/dismiss + delivery audit) without dragging in two other surfaces.
