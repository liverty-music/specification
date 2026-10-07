## Why

Event postponement (延期) was designed but never built. Nothing writes `events.rescheduled_at`; the backend entity notes that it stays nil until a postponement flow exists. So the `PostponementWindow` refund reason, the reschedule-time lookup and the proto field are code paths that never run, and specs describe behavior that cannot happen. The pilot launch (#1074) settled that a postponed show is handled as a cancellation followed by a new event, and that postponement is a future extension. Removing the dead surface now keeps the public event page, first-come sales and resale designs from planning around a state that does not exist.

## What Changes

- **BREAKING (proto):** remove `Event.rescheduled_time` (field 9) and the `RescheduledTime` message. Reserve the field number and name.
- **BREAKING (proto):** remove `RefundReason` `REFUND_REASON_POSTPONEMENT_WINDOW` (= 2) from the admin order service. Reserve the value and name. The admin console never sends it.
- Drop the comments in `order.proto`, `ticket.proto`, `settlement.proto`, `order_admin_service.proto` and `settlement_admin_service.proto` that list postponement as a refund or reversal cause.
- Backend:
  - Remove `Event.RescheduleTime`.
  - Remove `EventRescheduleTimeRepository` and its wiring.
  - Remove the `PostponementWindow` branch of the refund usecase.
  - Remove the related tests.
  - Add a migration that drops `events.rescheduled_at`. Every row is NULL, so no data is lost.
- Specs:
  - Remove the reschedule-time lookup and the postponement refund window.
  - Narrow refund reasons to Cancellation and Dispute.
  - Drop the "Event postponed" payout scenario.
- Kept as is: the payout gate still reads the event's start time on every run, and `Event.GetEventStartTime` still reads it afresh. A start time can be filled in after publish, so this behavior stands without postponement. Only the wording that justifies it by postponement changes.
- In-flight changes and docs that mention postponement are aligned:
  - `official-resale`: the "Event cancellation or postponement while listed" requirement becomes cancellation only.
  - `payments-legal-compliance`: the 返品特約 becomes "no returns except cancellation".
  - The `ticket-wallet-and-checkin` design note.
  - `docs/payments-design.md` refund taxonomy and `docs/resale-design.md`.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `components/usecase/order/refund-order`: reasons are Cancellation and Dispute only. The "Postponement refund window" requirement is removed. "Buyer refunded the full amount" no longer names PostponementWindow. The Purpose drops the postponement case.
- `components/entity/event/get-reschedule-time-by-order`: removed. Its only caller is the postponement refund window.
- `components/usecase/settlement/release-due-settlements`: the "Event postponed" scenario is removed. The requirement text no longer justifies the per-run start-time read by postponement; the behavior is unchanged.
- `components/entity/event` (Purpose): the "reschedule time" attribute row is removed.
- `components/entity/order` (Purpose): "refund reference" is empty unless refunded for a cancellation.
- `components/entity/event/get-event-start-time` (Purpose): the purpose sentence no longer mentions postponement; the requirement is unchanged.

`components/entity/order/create-refund` and `components/entity/order/commit-refund` are unchanged: they take no reason.

## Impact

- **specification:**
  - Breaking proto change, released with the `buf skip breaking` label. The BSR SDKs are regenerated.
  - Delta specs for the capabilities above.
  - Edits to the `official-resale`, `payments-legal-compliance` and `ticket-wallet-and-checkin` change artifacts and to two docs.
- **backend:**
  - `internal/entity/event.go`, `internal/entity/order.go`, `internal/entity/settlement.go`, `internal/entity/ticket.go` (comments).
  - `internal/usecase/refund_uc.go`, `internal/usecase/settlement_uc.go`, `internal/di/provider.go`.
  - `internal/infrastructure/database/rdb/event_reschedule_time_repo.go` (deleted).
  - `internal/adapter/rpc/mapper/settlement.go`.
  - `schema.sql` and a new Atlas migration dropping `events.rescheduled_at`.
  - Tests in `refund_uc_test.go` and `settlement_uc_test.go`.
  - The backend moves to the new schema release.
- **frontend:** no change. Nothing references postponement. It moves to the new schema release only when it next upgrades.
- **Prod:** the column drop runs through the existing `backend-migrations` AtlasMigration before fan-api rolls out. Nothing reads the column after the new release.
