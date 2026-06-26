## 1. Schema & migration (backend)

- [ ] 1.1 Add a `notifications` table to `internal/infrastructure/database/rdb/schema/schema.sql`: `id uuid pk`, `user_id`, `type`, `payload jsonb`, `created_at timestamptz`, `delivery_status` (`queued|sent|delivered|failed`), `delivered_at`, `failure_reason`, `read_at`, `dismissed_at`; index `(user_id, created_at desc)`.
- [ ] 1.2 Generate the Atlas migration (`atlas migrate diff --env local`), add the file to `k8s/atlas/base/kustomization.yaml` `configMapGenerator.files`, and verify with `atlas migrate apply --env local`.

## 2. Entity & repository (backend)

- [ ] 2.1 Define `entity.Notification` + `NotificationType` enum + `NotificationDeliveryStatus`, and the `entity.NotificationRepository` interface (`Create`, `UpdateDelivery`, `MarkRead`, `MarkDismissed`, `Get`, `ListByUser`).
- [ ] 2.2 Implement the pgx repository under `internal/infrastructure/database/rdb/notification_repo.go` (named columns, `$1/$2` placeholders, `pgx.RowToStructByName`); add an integration test.
- [ ] 2.3 Register the repository interface in `.mockery.yml` and run `mockery`.

## 3. Notification use case & outbox dispatch (backend)

- [ ] 3.1 Define `usecase.NotificationUseCase` (`Notify(ctx, userID, type, payload)`, `MarkRead`, `MarkDismissed`) and implement it: create the `queued` record, dispatch via the existing `entity.PushNotificationSender`, then update the row to `delivered`/`failed` with the result in hand.
- [ ] 3.2 Carry the `notification_id` into the dispatched push payload (`NotificationPayload.data.notification_id`).
- [ ] 3.3 On record-create failure, fall back to a best-effort send + log rather than dropping the notification (per design Decision 1 risk).
- [ ] 3.4 Wire the use case in the manual DI graph; unit-test the success / send-failure / record-failure / read-idempotency / cross-user-rejection paths.

## 4. Route existing producers through the service (backend)

- [ ] 4.1 Change `push_notification_uc.NotifyNewConcerts` to dispatch through `NotificationUseCase.Notify` (one record per recipient), preserving audience resolution and the 410-Gone subscription cleanup.
- [ ] 4.2 Change `sales_reminder_delivery_uc.DeliverReminder` to dispatch through `NotificationUseCase.Notify`, preserving once-only `RecordSent` semantics.
- [ ] 4.3 Confirm no notification source bypasses the service (grep for direct `PushNotificationSender.Send` call sites).

## 5. Read/dismiss surface

- [ ] 5.1 Expose `MarkRead` / `MarkDismissed` as a minimal Connect-RPC (e.g. `NotificationService.MarkRead`/`MarkDismissed`, taking `notification_id`, user-scoped via the auth context) — IN SCOPE, because the spec requirement "Read and dismiss state is user-controllable" cannot be satisfied without a control surface. Keep the proto delta to just these two user-scoped mutations; defer a full inbox `List` RPC to the inbox-UI follow-up.
- [ ] 5.2 Carry the `notification_id` end-to-end and verify the round-trip: stored id → push payload `data.notification_id` → service worker can read it (the SW *handler* that emits opened/dismissed is the analytics follow-up §7.1; this task only guarantees the id is present and correlatable).

## 6. Verification

- [ ] 6.1 `make check` passes (lint + migration + integration tests).
- [ ] 6.2 Manually verify (or integration-test) the end-to-end record → dispatch → delivery-state path for one new-concert and one sales-reminder notification, including a forced send-failure recording `failed`.

## 7. Documented follow-ups (NOT in this change)

- [ ] 7.1 Re-open `introduce-analytics-tool` tasks 13.2 (`notification.delivered`) and 5.7 (`notification.opened`/`dismissed`): emit on the `delivered` transition and from the SW `notificationclick`/`close` handler keyed by `notification_id` (Decision 14 of that change).
- [ ] 7.2 In-app notification **inbox / next-action** UI (frontend change) consuming `ListByUser` + read/dismiss.
- [ ] 7.3 Optional: split inline channel-state into a `notification_deliveries` child table when a second channel (email / in-app) is added.
