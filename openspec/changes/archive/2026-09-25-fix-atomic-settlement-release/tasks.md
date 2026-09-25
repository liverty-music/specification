# Tasks

## 1. Entity operation (components/entity/settlement/mark-released)

- [x] 1.1 Wrap `SettlementRepository.MarkReleased`'s status-flip UPDATE and every split's `transfer_ref` UPDATE in a single `pgx.Tx` (`Begin` / `defer Rollback` / `Commit`), keeping the existing `status = Held` guard as the transaction's first statement — verified by `go build ./...` and `make lint` (backend PR)
- [x] 1.2 Add `TestSettlementRepository_Integration` in `backend/internal/infrastructure/database/rdb/settlement_repo_test.go` covering:
  - `@spec components/entity/settlement/mark-released "Held settlement released"` and `"Already released or reversed"` — happy path flips status, persists the split's payout reference, and a second call on an already-Released settlement fails with FailedPrecondition
  - `@spec components/entity/settlement/mark-released "Unknown id"` — MarkReleased on a random id fails with FailedPrecondition
  - `@spec components/entity/settlement/mark-released "Failure changes nothing"` — a split update that violates `chk_settlement_splits_transfer_ref_not_empty` rolls back the whole transaction: the settlement stays Held, no charge reference or released time is recorded, and no split's payout reference is recorded; a retry with valid splits then succeeds
  - verified by `go test -tags=integration ./internal/infrastructure/database/rdb/... -run TestSettlementRepository_Integration`

## 2. Verification

- [x] 2.1 `make lint` and `go test ./internal/...` pass in the backend worktree (targeted integration test run in isolation from other agents' concurrent DB usage, per repo convention)
