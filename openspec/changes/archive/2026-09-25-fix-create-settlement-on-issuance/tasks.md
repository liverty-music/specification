## 1. Entity layer

- [x] 1.1 Add `Event.GetOrganizerID` (new minimal repository interface, consumed by `IssuanceUseCase`) resolving `event -> series -> organizer_id`; NotFound when the event is unknown or its series has no Organizer.
- [x] 1.2 Extend `IssuanceRepository.Issue` to accept a `*entity.Settlement` and insert it (and its splits) in the same transaction as the Order and Tickets.
- [x] 1.3 Remove `SettlementRepository.Upsert` (interface + rdb implementation + query) — unused once `EnsureSettlementExists` is gone.

## 2. Usecase layer

- [x] 2.1 `IssuanceUseCase.IssueFromCapturedWin` resolves the event's Organizer via `Event.GetOrganizerID`, builds a Held `Settlement` with one split (Organizer, full Order amount — platform fee stays `TODO(threshold)` per backend#778), and passes it to `Order.Issue`.
- [x] 2.2 Remove `PayoutSweeperUseCase.EnsureSettlementExists` (interface + implementation) — dead code, no production caller.

## 3. Infrastructure / DI

- [x] 3.1 Implement `internal/infrastructure/database/rdb/event_organizer_repo.go` (mirrors `event_start_time_repo.go`'s minimal-repository pattern).
- [x] 3.2 Wire `NewEventOrganizerRepository` into `internal/di/provider.go` and pass it into `NewIssuanceUseCase`.
- [x] 3.3 Regenerate mocks with `mockery` if any mockery-tracked interface signature changed. (`mockery` currently fails repo-wide on `internal/entity` — pre-existing, unrelated tooling bug; no mock file was affected.)

## 4. Tests

- [x] 4.1 Usecase-level test (fakes/mocks) that follows an Order from `IssueFromCapturedWin` through to a Settlement `ReleaseDueSettlements` can actually release. (`TestIssuanceUseCase_ThroughSettlementRelease`)
- [x] 4.2 Integration test on `IssuanceRepository.Issue` against a real local Postgres asserting the Order, Tickets, Settlement and its split are all committed atomically, and that a failure leaves none of them. (`TestIssuanceRepository_Integration`, `TestIssuanceRepository_Issue_FailureStoresNothing`)
- [x] 4.3 Update/remove the now-gone `EnsureSettlementExists` test cases in `internal/usecase/settlement_uc_test.go`. (None existed — nothing in production or tests ever called it; only the now-dead `stubSettlementRepo.Upsert` method was removed.)

## 5. Known-defect note

- [x] 5.1 `stories/win-tickets-in-a-lottery` delta drops the `Known defect: liverty-music/backend#468` note (the requirement and scenario are otherwise unchanged); confirm no other `grep -rn "backend#468" openspec/specs/` hits remain after archive.

## 6. Scenario coverage

- [x] 6.1 Annotate backend tests with `@spec <capability-path> "<scenario>"` for every ADDED/MODIFIED scenario in this change's delta specs. Verified with `python3 scripts/check-scenario-coverage.py fix-create-settlement-on-issuance --repos <backend-worktree>` → 13/13 covered.

Post-archive follow-up (not gated on this checklist — the empty files below don't exist until archive runs):
After `openspec archive`, check whether `specs/components/usecase/settlement/ensure-settlement-exists/spec.md` and `specs/components/entity/settlement/upsert/spec.md` were left with an empty `## Requirements` section (their only requirement was REMOVED); if so, delete those now-empty capability spec files/directories as a follow-up commit.
