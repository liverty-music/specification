# Tasks

## 1. Proto (specification → BSR)

- [x] 1.1 Delete `Event.rescheduled_time` and add `reserved 9; reserved "rescheduled_time";` in `event.proto`. Delete the `RescheduledTime` message from `entity.proto`. Verify with `git grep -n RescheduledTime proto`, which returns nothing.
- [x] 1.2 Delete `REFUND_REASON_POSTPONEMENT_WINDOW` and add `reserved 2; reserved "REFUND_REASON_POSTPONEMENT_WINDOW";` to `RefundReason`. Reword the `OrderAdminService` and `RefundOrder` comments so they name only cancellation (中止) and dispute, and drop the postponement-window FAILED_PRECONDITION case. Verify that the `RefundOrderRequest.reason` validation (`defined_only`, `not_in: [0]`) is unchanged.
- [x] 1.3 Reword the postponement mentions in `order.proto`, `ticket.proto` (Voided comment, `event_id` comment), `settlement.proto` and `settlement_admin_service.proto`. Verify with `git grep -n -i -E "postpon|reschedul|延期" proto`, which returns nothing.
- [x] 1.4 Run `buf format -w`, `buf lint` and `buf breaking`. Verify that `buf breaking` reports only the removed field, enum value and message.

## 2. In-flight changes and docs (specification)

- [x] 2.1 `official-resale`:
  - Rename the requirement to "Event cancellation while listed" and drop its postponement text and scenario.
  - Drop the postponement bullet in its proposal and the Capabilities line wording.
  - Drop "postponement paths" from task 8.2.
  - Verify with `openspec validate official-resale --strict`.
- [x] 2.2 `payments-legal-compliance`: make the 返品特約 read "no returns except event cancellation (中止)" in the proposal, task 2.2 and `specs/components/infrastructure/fan/web/route/order/spec.md`. Verify with `openspec validate payments-legal-compliance --strict`.
- [x] 2.3 `ticket-wallet-and-checkin`:
  - In `entity/event/get`, rewrite the Purpose to "a date or time filled in after publish". Replace the "Postponed event" scenario with "Start time filled in later".
  - Drop the postponed-window sentence from the `reception-link` "Reception window" requirement.
  - Reword the design note at the reception-window decision.
  - Verify with `openspec validate ticket-wallet-and-checkin --strict`.
- [x] 2.4 Rewrite the refund taxonomy and the 返品特約 wording in `docs/payments-design.md`, and item 9 in `docs/resale-design.md`, to cancellation only. Verify with `git grep -n -i postpon docs openspec/changes -- ':!openspec/changes/archive' ':!openspec/changes/remove-event-postponement' ':!openspec/changes/public-event-page'`, which returns nothing.
- [x] 2.5 Open the specification PR with the `buf skip breaking` label, staging only the paths from 1.x and 2.x by name. After merge, cut the next minor GitHub Release. Verify with `gh run list --repo liverty-music/specification --workflow buf-release.yml --limit 3`, which shows BSR generation succeeded.

## 3. Backend: refund usecase (components/usecase/order/refund-order, components/entity/event/get-reschedule-time-by-order)

- [x] 3.1 Upgrade the schema package to the new release following the `consume-proto-release` skill. Verify that `go build ./...` fails only at `mapper/settlement.go` on the removed `REFUND_REASON_POSTPONEMENT_WINDOW`.
- [x] 3.2 Remove the `RefundReasonPostponementWindow` case from `ProtoRefundReasonToDomain`. Verify the mapper test (or a new table case) maps an undefined value to `RefundReasonUnspecified`.
- [x] 3.3 In `internal/usecase/refund_uc.go`:
  - Delete `RefundReasonPostponementWindow` and its `String` case, `PostponementRefundWindow`, the `EventRescheduleTimeRepository` interface, the `rescheduleTimeRepo` field and constructor parameter, and the window gate.
  - Reword the interface and refund-amount comments to Cancellation and Dispute.
  - Keep `Cancellation = 1` and `Dispute = 3`.
- [x] 3.4 Delete `internal/infrastructure/database/rdb/event_reschedule_time_repo.go` and its wiring in `internal/di/provider.go`. Verify with `go build ./...`.
- [x] 3.5 In `refund_uc_test.go`:
  - Delete the `stubEventRescheduleTimeRepo` stub and the PostponementWindow tests, and update the constructor calls.
  - Keep the tests for "Reason missing", "Repeated refund", "Unknown order", "Cancellation refund", "Dispute", the claw-back scenarios and the "Refund recorded" scenarios.
  - Verify with `go test ./internal/usecase/... -run Refund`.

## 4. Backend: entity, payout gate and schema (components/usecase/settlement/release-due-settlements)

- [x] 4.1 Delete `entity.Event.RescheduleTime`. Reword the postponement comments in `internal/entity/order.go`, `ticket.go` and `settlement.go` (`IsReleaseEligible`: the start time is read afresh because it can be filled in after publish), and in `internal/usecase/settlement_uc.go`. Verify with `git grep -n -i -E "postpon|reschedul" -- internal`, which returns nothing.
- [x] 4.2 In `settlement_uc_test.go`, rename the two postponement cases so they describe a start time that is later than at purchase. Add or confirm unit tests for the scenarios "Before the event plus 7 days", "Event start unknown" and "Start time filled in after the purchase" with the operations mocked. Verify with `go test ./internal/usecase/... -run Settlement` and `go test ./internal/entity/...`.
- [x] 4.3 Remove `rescheduled_at` and its `COMMENT` from `schema/schema.sql`, update the `orders.refund_ref` comment to drop POSTPONEMENT_WINDOW, and run `atlas migrate diff --env local drop_events_rescheduled_at`. Add the new file to `k8s/atlas/base/kustomization.yaml` following the `db-migration-workflow` skill. Verify with `atlas migrate apply --env local` and with `\d events`, which shows no `rescheduled_at`.
- [x] 4.4 Run `make check`. Open the backend PR with the OpenSpec-Change field and the store commit SHA filled in. Verify that CI is green.

## 5. Release verification and close-out (specification)

- [x] 5.1 After the backend release, confirm in prod that the `backend-migrations` AtlasMigration applied the drop and that `events` has no `rescheduled_at`, and that the API workloads run the new release with no errors. The Cancellation refund path is covered by the refund use-case unit tests and the Stripe Sandbox E2E (`MoneyOut`) rather than by a manual dev refund, because the dev environment is suspended indefinitely.
- [x] 5.2 At archive, edit the main-spec Purposes that a delta cannot change:
  - `components/entity/event` drops the "reschedule time" row.
  - `components/entity/order` makes the "refund reference" row read "empty unless refunded for a cancellation".
  - `components/entity/event/get-event-start-time` drops the postponement clause.
  - `components/usecase/order/refund-order` names only 中止 (cancellation) and dispute.
  - Delete the emptied `components/entity/event/get-reschedule-time-by-order` spec.
  - Verify with `openspec validate --specs --strict`.
