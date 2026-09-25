## Why

No production code ever creates a Settlement, so `ReleaseDueSettlements` always scans an empty `ListHeld` and Organizers are never paid out (backend#468). `PayoutSweeperUseCase.EnsureSettlementExists` was meant to backfill the missing row but nothing calls it, and `Settlement.Upsert` (its only caller) is unused. The fix is to record the Held Settlement as part of issuance itself, the moment the Order and its Tickets are stored, so a Settlement exists for every issued Order without a separate sweep step.

## What Changes

- `Order.Issue` now stores a Held Settlement, with one split paying the event's Organizer, in the same transaction as the Order and its Tickets — atomic, so an issued Order is never left without its Settlement.
- `IssuanceUseCase.IssueFromCapturedWin` resolves the event's Organizer (via the phase's event and its series) and builds the Settlement it hands to `Order.Issue`. The split amount is the Order's full amount; the platform fee rate is `TODO(threshold)` pending business decision backend#778, so the interim fee is 0 (unchanged from the existing `EnsureSettlementExists` spec's placeholder).
- **REMOVED**: `PayoutSweeperUseCase.EnsureSettlementExists` — superseded by `Order.Issue`. Nothing in production ever called it.
- **REMOVED**: `Settlement.Upsert` — its only caller was `EnsureSettlementExists`; `Order.Issue` inserts the Settlement directly.
- New entity operation `Event.GetOrganizerID`, resolving the Organizer that owns an Event via its Series, consumed by `IssueFromCapturedWin`.

## Capabilities

### New Capabilities

- `components/entity/event/get-organizer-id`: Resolves the Organizer that owns an Event via its Series, so the issuance path can stamp the Settlement's Organizer.

### Modified Capabilities

- `components/entity/order/issue`: Issue also stores a Held Settlement (one Organizer split) atomically with the Order and Tickets.
- `components/usecase/order/issue-from-captured-win`: Resolves the event's Organizer and builds the Held Settlement passed to `Order.Issue`.
- `components/usecase/settlement/ensure-settlement-exists`: REMOVED — superseded by `Order.Issue`.
- `components/entity/settlement/upsert`: REMOVED — no longer called; `Order.Issue` is the sole settlement-creation path.

## Impact

- **backend**: `internal/entity/order.go` (`IssuanceRepository.Issue` signature), `internal/infrastructure/database/rdb/issuance_repo.go` (settlement + split insert in the issuance transaction), `internal/infrastructure/database/rdb/event_organizer_repo.go` (new), `internal/usecase/issuance_uc.go` (`EventOrganizerRepository` port + Settlement construction), `internal/usecase/settlement_uc.go` / `settlement_port.go` (remove `EnsureSettlementExists`), `internal/entity/settlement.go` / `internal/infrastructure/database/rdb/settlement_repo.go` (remove `Upsert`), `internal/di/provider.go` (wiring). Tests: `internal/usecase/issuance_uc_test.go` (usecase-level, follows an Order from issuance through a released Settlement with fakes), `internal/infrastructure/database/rdb/issuance_repo_test.go` (integration test for the atomic transaction), `internal/usecase/settlement_uc_test.go` (removes the now-gone `EnsureSettlementExists` cases).
- No proto/schema change — `settlements` and `settlement_splits` already exist (migration `20260914000000_add_settlement_payout_tables.sql`); this only adds the missing write path.
