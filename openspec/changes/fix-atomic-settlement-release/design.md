## Context

`SettlementRepository.MarkReleased` (`backend/internal/infrastructure/database/rdb/settlement_repo.go`) currently issues the `settlements` status-flip `UPDATE` and each `settlement_splits` `UPDATE` as separate, ungrouped `pgx.Pool.Exec` calls. A failure on any split update after the status update already committed leaves the two out of sync. The sibling operation `RefundRepository.CommitRefund` (`refund_repo.go`) already writes a Settlement's status and its splits — plus the Order and its Tickets — inside one `pgx.Tx`, guarded by `defer tx.Rollback(ctx)` after `tx.Commit(ctx)` succeeds (a no-op post-commit). `IssuanceRepository.Issue` follows the identical shape for the Order+Tickets write. This change conforms `MarkReleased` to that existing pattern; no new pattern is introduced.

## Goals / Non-Goals

**Goals:**
- `MarkReleased`'s status flip and every split's `transfer_ref` update commit as one atomic unit, matching the "all together or not at all" requirement in this change's spec delta.
- Follow the existing `pgx.Pool.Begin` / `defer tx.Rollback` / `tx.Commit` shape already used by `CommitRefund` and `Issue` — no new transaction helper.

**Non-Goals:**
- Creating `settlement_splits` rows (populating splits for a newly-created Settlement) is out of scope — that is backend#468, fixed in parallel.
- No change to `MarkReleased`'s Go signature, its interface (`entity.SettlementRepository`), or the calling usecase (`settlement_uc.go`).
- No new transactor/unit-of-work abstraction spanning the usecase boundary — the transaction stays fully inside the repository method, as it already does in `CommitRefund` and `Issue`.

## Decisions

- **Wrap the existing two statements in one `pgx.Tx`, opened and committed inside `MarkReleased`.** Alternative considered: introduce a generic transactor pattern where the usecase controls the transaction boundary and passes it down via context. Rejected because no other write path in this codebase does that yet (`CommitRefund` and `Issue` both scope the transaction to the repository method), and introducing a new pattern for one bug fix would be inconsistent with the rest of `rdb/`.
- **The `status = Held` guard (`WHERE id = $1 AND status = 1`) stays as the first statement inside the transaction**, so a concurrent release attempt still finds `RowsAffected() == 0` and returns `FailedPrecondition` — behavior unchanged from today, just now transactionally isolated from the split writes that follow it.
- **Errors keep surfacing through the existing `toAppErr` mapping** (e.g., a `settlement_splits` CHECK-constraint violation → `InvalidArgument`); the transaction wrapper changes nothing about error classification, only about what gets persisted before the error is returned.

## Risks / Trade-offs

- [A split update failing after the status update inside the same transaction still charges the DB round-trips already spent before rollback] → Acceptable: this was already the failure-visible cost path (the bug), and the fix trades a small amount of wasted work in the failure case for correctness; the happy path issues the same number of statements as before.
- [Longer-held transaction/connection while N splits are updated] → MVP has exactly one split per Settlement (per `entity/settlement/spec.md`), so N is 1 in practice; even with future multi-payee splits the row count stays small (one row per payee), matching `CommitRefund`'s already-accepted shape.
