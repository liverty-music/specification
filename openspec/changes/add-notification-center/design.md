## Context

See proposal.md (Why). Current state the design builds on:

- `notifications` stores the rendered push (`payload` JSONB: title, body, tag, data) and its delivery state (`delivery_status`, `failure_reason`, `queued_at`, `delivered_at`) plus `read_at` and `dismissed_at`. In production all 101 rows have `read_at` and `dismissed_at` NULL: no client calls `MarkRead` or `Dismiss`.
- Each push sender renders its own copy in its own file (`ticket_sale_copy.go`, `notification_new_concerts.go`, `order_confirmation.go`, `lottery_loss.go`, `resale_entry_ended.go`, `event_cancelled.go`, `order_refunded.go`) and passes a finished `NotificationPayload` as the `deliver-notification` workflow input (`DeliverRequest.Payload`).
- `UpdateDelivery` announces `NOTIFICATION.delivered`; the analytics consumer turns it into the PostHog event `notification.delivered`. No saved PostHog insight uses that event. Delivery rates are computed by the BigQuery view `mart_pipeline_health_daily.sql` (cloud-provisioning) from the analytics log lines of topic `notification_delivery`, which `notification_delivery.go` writes for every outcome.
- `queued_at` and `delivered_at` differ by at most 5.6 seconds in production: the record is created right before the send.

## Goals / Non-Goals

**Goals:** one renderer for every push and for the notification center; a `notifications` table that holds only what the fan sees (type, subject, create time, read time).

**Non-Goals:** a retention or deletion job for notifications; an "all read" action; per-type notification settings; changing any email.

## Decisions

### The entity renders the message; the usecase loads the records

`Notification.Message(lang string, s *LoadedSubject) *NotificationPayload` in `internal/entity` renders title, body, link and tag from already-loaded records. It reads nothing and holds no clock: `LoadedSubject` carries the records the subject names (Artist, Concerts with Series, Venue and Artists, TicketSale, Order, LotteryEntry, ResaleEntry), the fan's follows with their hype, the fan's time zone and `Now` (read by the usecase, for the "resale is still open" condition). The copy table lives next to it as a map keyed by case and language, like `ticketSaleCopies` today. Placing it on the entity follows the existing pure methods (`Hype.MatchingConcerts`); the usecase layer keeps one loader, `loadSubject(ctx, user, n)`, used by both `Deliver` and `List`.

Alternative rejected: rendering in each usecase (today's shape). It is what made the copy drift between types.

### The subject is one JSONB column

`notifications.subject JSONB NOT NULL` with fixed keys: `artist_id`, `event_ids`, `event_id`, `ticket_sale_id`, `stage`, `order_id`, `lottery_entry_id`, `resale_entry_id`. `entity.NotificationSubject` holds them, with `json` tags (it is also the workflow input, see below), and `Validate(type)` implements the entity rule "The subject names exactly what the type is about".

Alternative rejected: one nullable foreign-key column per record kind. Eight columns, mostly NULL, and foreign keys would block deleting an Event with its Orders, which the cancellation flow already handles as NotFound. A missing record is handled at read time instead: `Deliver` sends nothing and `List` leaves the row out.

### List renders each row on the fly, without batching

`NotificationUseCase.List` reads `ListByUser(user, 50)`, the fan's follows once, then loads each row's subject one by one. At 50 rows this is at most a few hundred point reads, run only when a fan opens the app or the center. Batching by type (`ListByIDs` per record kind) is the fallback if the RPC's latency shows it is needed; it changes no spec.

### What each screen value is read from

`NotificationService.List` returns `repeated entity.v1.Notification`. The center and the bell read:

| value | RPC field |
|---|---|
| title, body | `Notification.message.title`, `.body` (rendered by the server) |
| link | `Notification.message.data["url"]` |
| sent time | `Notification.create_time` |
| read or unread, bell count | `Notification.read_time` present or absent |

### Proto

- `entity.v1.Notification`: keep `id`, `user_id`, `type`, `message` (now rendered at read time); rename field 7 `queue_time` to `create_time`; keep `read_time` (9); remove and reserve `delivery_status` (5), `failure_reason` (6), `deliver_time` (8), `dismiss_time` (10). Remove `NotificationDeliveryStatus`.
- `NotificationType`: rename `EVENT_CANCELLED = 8` to `CONCERT_CANCELLED`, keeping the number; add `LOTTERY_WIN = 10`; reserve `4` and the name `NOTIFICATION_TYPE_ORDER_CONFIRMATION`.
- `rpc.notification.v1.NotificationService`: add `List(ListRequest) returns (ListResponse)` (`ListRequest {}`; `ListResponse { repeated entity.v1.Notification notifications = 1; }`); remove `Dismiss` and its messages. Names follow `rpc-design`: `List` returns every resource the caller can see.
- `rpc.user.v1.CreateRequest.preferred_language`: drop `optional`, mark `required`, keep the pattern.

The PR takes the `buf skip breaking` label.

### Delivery outcome: returned and logged, not stored

`Deliver` keeps computing Delivered or Failed and returns it (DeliverReminder needs it), keeps the metric and the analytics log lines unchanged, and stops calling `UpdateDelivery`. Removed: `NotificationRepository.UpdateDelivery`, `entity.SubjectNotificationDelivered` and its entry in the subject list, the consumer route `track-notification-delivered` and `AnalyticsConsumer.HandleNotificationDelivered`, `usecase.EventNotificationDelivered`. The BigQuery mart is unaffected.

### Deliver input and workflow

`DeliverRequest` becomes `{UserID, Type, Subject}`. `DeliverReminder`'s input drops its prepared content for the linked event id. The order of `Deliver`'s steps becomes: load subject and render (one step), `Notification.Create`, send, log. No `f.Patched` compatibility branch: the product has no users, and the deploy waits for no pending run instead (Migration Plan).

### Headline artist

For new_concerts the subject's artist. Otherwise `Concert.Artists` (display order) ranked by the fan's hype from `FollowRepository.ListByUser` (Away > Nearby > Home > Watch), first in display order on ties or when the fan follows none.

### Removing the result-day reminder

`ReminderStageResultDay` goes from the entity enum, the scan's stage set and its audience branch; `TicketJourneyRepository.ListUserIDsAppliedSeries` and the result-date clause of `ListWithPendingMilestones` go with it. `TicketSale.result_date` itself stays: discovery still records it and the other TicketSale specs still describe it.

### First-come purchase push and the type rename

`SendOrderConfirmation` starts `Deliver` only when `order.LotteryEntryID != ""`, with type `lottery_win` and the workflow id `deliver:lottery_win:<order>`. `event_cancelled` is renamed `concert_cancelled` everywhere (proto enum value, entity constant, workflow id prefix, analytics `type` values). Production holds no row of either old value that must survive (rows are deleted, below).

### Marking a push read when opened

The Service Worker's `notificationclick` appends `notification=<notification_id>` to the target URL. The app shell reads the parameter after each navigation, calls `NotificationService.MarkRead` when a fan is signed in, refreshes the bell, and removes the parameter with `history.replaceState`. The Service Worker itself cannot call the RPC: it holds no access token.

### Bell and center in the fan web app

A small store service owns the last `List` response and the unread count; the bell (in the shell header's `au-slot` of `page-header`) and the `/notifications` route read it. It refreshes on start, on `visibilitychange` to visible, and after `MarkRead`. `/notifications` is a protected route, not a bottom-nav tab; its title comes from its route configuration like every other route.

### Preferred language required

`users.preferred_language` becomes `NOT NULL` (production has no NULL). `UserUseCase.Create` validates it; the frontend already sends it from `auth-callback-route.ts`, and the "Legacy NULL row" backfill in `user-hydration-task.ts` and the NULL handling in `user-store.ts` go. The email specs' "(Japanese when none)" clauses become unreachable; they are left as they are, because emails are out of scope.

## Risks / Trade-offs

- [A record deleted after the push makes its notification vanish from the center] → Only test data is ever deleted (an Event deleted with its Orders); acceptable.
- [Text in the center can differ from the push the fan saw, when a sale time or venue is corrected] → Intended: the center shows the current facts.
- [List latency with 50 point-read rows] → Batch by record kind if the RPC's p95 shows it.
- [A pending `deliver-notification` or `deliver-reminder` run with the old input fails after the deploy and pages an admin] → Check for pending runs before deploying (Migration Plan); with no users there are normally none.

## Migration Plan

1. Release the proto (specification PR, GitHub Release, BSR generation).
2. Backend: one Atlas migration that deletes every `notifications` row, drops `payload`, `delivery_status`, `failure_reason`, `delivered_at`, `dismissed_at` and their constraints, adds `subject JSONB NOT NULL`, renames `queued_at` to `created_at` (and its index), sets `users.preferred_language NOT NULL`, deletes `ticket_sale_reminders` rows of stage `RESULT_DAY` and narrows that table's stage check. Before deploying, list pending `deliver-notification` and `deliver-reminder` workflows read-only (cloud-provisioning runbook `workflow-needs-admin.md`); deploy when none is pending.
3. Frontend after the backend is live (it calls `List`).
Rollback: revert the deploys; the deleted notification rows are test data and are not restored.
