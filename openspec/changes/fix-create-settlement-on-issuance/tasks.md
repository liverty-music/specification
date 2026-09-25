## 1. Entity layer

- [ ] 1.1 Add `Event.GetOrganizerID` (new minimal repository interface, consumed by `IssuanceUseCase`) resolving `event -> series -> organizer_id`; NotFound when the event is unknown or its series has no Organizer.
- [ ] 1.2 Extend `IssuanceRepository.Issue` to accept a `*entity.Settlement` and insert it (and its splits) in the same transaction as the Order and Tickets.
- [ ] 1.3 Remove `SettlementRepository.Upsert` (interface + rdb implementation + query) — unused once `EnsureSettlementExists` is gone.

## 2. Usecase layer

- [ ] 2.1 `IssuanceUseCase.IssueFromCapturedWin` resolves the event's Organizer via `Event.GetOrganizerID`, builds a Held `Settlement` with one split (Organizer, full Order amount — platform fee stays `TODO(threshold)` per backend#778), and passes it to `Order.Issue`.
- [ ] 2.2 Remove `PayoutSweeperUseCase.EnsureSettlementExists` (interface + implementation) — dead code, no production caller.

## 3. Infrastructure / DI

- [ ] 3.1 Implement `internal/infrastructure/database/rdb/event_organizer_repo.go` (mirrors `event_start_time_repo.go`'s minimal-repository pattern).
- [ ] 3.2 Wire `NewEventOrganizerRepository` into `internal/di/provider.go` and pass it into `NewIssuanceUseCase`.
- [ ] 3.3 Regenerate mocks with `mockery` if any mockery-tracked interface signature changed.

## 4. Tests

- [ ] 4.1 Usecase-level test (fakes/mocks) that follows an Order from `IssueFromCapturedWin` through to a Settlement `ReleaseDueSettlements` can actually release.
- [ ] 4.2 Integration test on `IssuanceRepository.Issue` against a real local Postgres asserting the Order, Tickets, Settlement and its split are all committed atomically, and that a failure leaves none of them.
- [ ] 4.3 Update/remove the now-gone `EnsureSettlementExists` test cases in `internal/usecase/settlement_uc_test.go`.

## 5. Known-defect note

- [ ] 5.1 `stories/win-tickets-in-a-lottery` delta drops the `Known defect: liverty-music/backend#468` note (the requirement and scenario are otherwise unchanged); confirm no other `grep -rn "backend#468" openspec/specs/` hits remain after archive.

## 6. Archive cleanup (after the backend PR merges)

- [ ] 6.1 After `openspec archive`, check whether `specs/components/usecase/settlement/ensure-settlement-exists/spec.md` and `specs/components/entity/settlement/upsert/spec.md` were left with an empty `## Requirements` section (their only requirement was REMOVED); if so, delete those now-empty capability spec files/directories as a follow-up commit.
