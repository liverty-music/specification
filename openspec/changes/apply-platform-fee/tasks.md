# Tasks

## 1. Entity (components/entity/settlement)

- [x] 1.1 Add a named `entity.PlatformFee(amountJPY int64) int64` function near the Settlement entity implementing `floor(amount × 5 ÷ 100)` with integer arithmetic, and verify one unit test per scenario passes: `@spec components/entity/settlement "Round order amount"`, `@spec components/entity/settlement "Amount that does not divide evenly"`, `@spec components/entity/settlement "Fee rounds down to zero"`.
- [x] 1.2 Verify the existing split-invariant tests still cover the refreshed "Splits and platform fee" example scenarios (no rate is enforced there — the requirement is a generic invariant over whatever splits a Settlement carries) with `@spec components/entity/settlement "Single Organizer split"`, `@spec components/entity/settlement "No split"`, `@spec components/entity/settlement "Non-positive split"`, `@spec components/entity/settlement "Splits exceed the order"`.

## 2. Entity operation (components/entity/order/issue)

- [x] 2.1 No implementation change: `Order.Issue` stores whatever Settlement it is given atomically; the fee is computed by the caller (IssuanceUseCase), not by Issue itself. Confirm the existing `@spec components/entity/order/issue` annotations in `internal/infrastructure/database/rdb/issuance_repo_test.go` still cover "Order issued", "Failure stores nothing" and "Second order for the application" (scenario text unchanged by this delta).

## 3. Usecase (components/usecase/order/issue-from-captured-win)

- [x] 3.1 In `internal/usecase/issuance_uc.go`, compute the Organizer's Held Settlement split as `order.Amount - entity.PlatformFee(order.Amount)` instead of `order.Amount`; drop the `TODO(threshold)` comment and its `backend#778` reference (correct to `liverty-music/specification#778`).
- [x] 3.2 Update `internal/usecase/issuance_uc_test.go` to assert the fee-adjusted split amount, and verify `@spec components/usecase/order/issue-from-captured-win "Won application issued"` (16000 yen order → 15200 yen split) still passes together with the other scenarios of the same (modified) requirement: "Replayed issuance", "Concurrent issuance", "Application not won", "Payment not captured", "Organizer unresolved".

## 4. Verification

- [x] 4.1 `openspec validate apply-platform-fee --strict` passes.
- [x] 4.2 `python3 scripts/check-scenario-coverage.py apply-platform-fee --repos ../backend` reports full coverage.
- [x] 4.3 Backend `make lint` and targeted `go test ./internal/entity/... ./internal/usecase/...` pass.
