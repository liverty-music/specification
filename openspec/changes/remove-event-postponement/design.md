## Context

See proposal.md - Why. The postponement surface spans three repositories and one table:

- **specification:** `Event.rescheduled_time` (field 9, `OUTPUT_ONLY`) and the `RescheduledTime` value message in `entity.proto`. `RefundReason.REFUND_REASON_POSTPONEMENT_WINDOW = 2` in `order_admin_service.proto`. `RefundOrderRequest.reason` is validated with `defined_only: true, not_in: [0]`.
- **backend:**
  - `usecase.RefundReasonPostponementWindow` (= 2), `PostponementRefundWindow` (14 days) and the `EventRescheduleTimeRepository` interface live in `internal/usecase/refund_uc.go`. The interface is realized by `rdb.EventRescheduleTimeRepository`, which reads `events.rescheduled_at`.
  - `entity.Event.RescheduleTime` is never populated. No event repository query selects `rescheduled_at`, and the event mapper does not emit `rescheduled_time`.
  - `mapper.ProtoRefundReasonToDomain` maps the proto value 2 to the domain value.
  - `events.rescheduled_at` was added by `k8s/atlas/base/migrations/20260915000000_add_events_rescheduled_at.sql` and is NULL in every row.
- **frontend:** no reference to either proto symbol.

The payout gate (`entity.IsReleaseEligible`, `settlement_uc.go`) reads the event's start time on every sweep. Its comments justify this with postponement, but the read is still needed because a start time can be filled in after publish.

## Goals / Non-Goals

**Goals:**
- Remove every postponement code path, proto symbol and column in one coordinated release, without renumbering anything that stays.
- Keep the refund and payout behavior for Cancellation and Dispute identical.

**Non-Goals:**
- Designing a future postponement flow. If one comes back, it is a new change and may reuse nothing here.
- Changing how an Event's date or times are edited.
- Upgrading the frontend's schema package; it moves to the new release on its next routine upgrade.

## Decisions

### Reserve, don't renumber

`Event` gets `reserved 9; reserved "rescheduled_time";`, and `RefundReason` gets `reserved 2; reserved "REFUND_REASON_POSTPONEMENT_WINDOW";`. `RescheduledTime` is deleted outright: it is used only by field 9, and message names need no reservation. The domain `RefundReason` keeps `Cancellation = 1` and `Dispute = 3` so it still mirrors the proto numbers.

*Alternative:* deprecate the field and the value (`deprecated = true`) and remove them later. Rejected: nothing populates or sends either one, so a deprecation period protects no caller and leaves a second change to schedule.

### Old admin clients are rejected at the boundary

An admin console built against the old schema could still send the number 2. `defined_only: true` rejects it with InvalidArgument before the handler runs. If it ever got through, `ProtoRefundReasonToDomain` maps any unknown value to `RefundReasonUnspecified`, which the usecase also rejects with InvalidArgument. No extra guard is needed. The admin console never sends 2 today.

### The refund usecase loses a dependency

`NewRefundOrderUseCase` drops its `EventRescheduleTimeRepository` parameter. The interface, the `rdb` implementation file and its wiring in `internal/di/provider.go` are deleted together. The `PostponementWindow` branch, `PostponementRefundWindow` and the "postponement path" remark in the refund-amount comment go too. The `refund_uc_test.go` stub and its window tests are deleted. Cancellation and Dispute tests are kept unchanged and serve as the regression check.

### The column is dropped in the same release

`schema.sql` loses `rescheduled_at` and its `COMMENT`. `atlas migrate diff --env local drop_events_rescheduled_at` generates `ALTER TABLE events DROP COLUMN rescheduled_at`, and the file is added to `k8s/atlas/base/kustomization.yaml` per the `db-migration-workflow` skill. The `AtlasMigration` runs at sync-wave 1, before the fan-api Deployment. During rollout the old pods still hold the `rdb.EventRescheduleTimeRepository` query, but it runs only for a `POSTPONEMENT_WINDOW` refund, which nobody sends. No other query names the column.

*Alternative:* ship the code removal first and drop the column in a later release (expand/contract). Rejected: the column is already unread outside a path that never runs, so the two-step release buys no safety.

### Spec deltas

`refund-order` uses MODIFIED for the two requirements whose text changes, and REMOVED for the window requirement. `release-due-settlements` cannot use MODIFIED: a MODIFIED block must keep every existing scenario, and the "Event postponed" scenario has to go. So the requirement is REMOVED and re-ADDED as "Release 7 days after the event's current start", with the same gate and a scenario for a start time filled in after the purchase. `get-reschedule-time-by-order` has its only requirement REMOVED.

Purpose sections cannot be changed by a delta. The Purpose edits listed in the proposal go into the main specs at close-out, together with deleting the then-empty `get-reschedule-time-by-order` spec directory (tasks section 5).

### In-flight changes are reworded, not restructured

- `official-resale`: "Event cancellation or postponement while listed" becomes "Event cancellation while listed". Its postponement scenario, the proposal bullet and task 8.2's "postponement paths" are dropped.
- `payments-legal-compliance`: the 返品特約 (returns clause) reads "no returns except event cancellation (中止)" in the proposal, task 2.2 and the route/order spec.
- `ticket-wallet-and-checkin`:
  - `entity/event/get` Purpose says "read afresh so that a date or time filled in after publish is seen at once". Its "Postponed event" scenario becomes "Start time filled in later".
  - The `reception-link` sentence about a postponed event's window is dropped; the requirement already derives the window from the current date and times.
  - The design note says "so a time filled in later moves it".
- `public-event-page` already defers to this change and needs no edit.
- In `docs/payments-design.md` and `docs/resale-design.md`, the refund taxonomy reads "cancellation (中止) only; a postponed show is cancelled and re-listed as a new event".

## Risks / Trade-offs

- [The breaking proto change fails `buf breaking` in CI] → Release it with the `buf skip breaking` label, as the proposal states.
- [A future postponement feature needs the column back] → It would be a new nullable column added by a new migration. Nothing is lost, because every row is NULL today.
- [Editing other changes' artifacts in the shared store working tree collides with their sessions] → Edit only the listed files, and stage them by path when the specification PR is cut.

## Migration Plan

1. specification:
   - Remove the proto symbols and reword the comments.
   - Edit the in-flight changes and docs.
   - Merge with the `buf skip breaking` label.
   - Cut the next minor release and wait for BSR generation.
2. backend:
   - Upgrade the schema package (`consume-proto-release`).
   - Remove the code and add the migration.
   - Merge. ArgoCD applies the migration (sync-wave 1) before rolling out fan-api.
3. Verify in prod: `\d events` shows no `rescheduled_at`; an admin Cancellation refund still succeeds in dev.

Rollback: revert the backend PR, and add a forward migration that re-adds the nullable column if the old code must run again. The old code only reads the column on the unused path, so a rollback without re-adding it fails only for a `POSTPONEMENT_WINDOW` refund, which nobody sends.
