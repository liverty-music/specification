## Why

`Settlement.MarkReleased`'s spec only guarantees "changes nothing" for its two enumerated guard failures (not Held, unknown id). It is silent on what happens if recording a split's payout reference fails for any other reason (e.g. a constraint violation) after the status has already been flipped to Released — the implementation split that write across two ungrouped statements, so such a failure could leave a settlement Released with a split missing its transfer reference, or the reverse. `Order.CommitRefund`, the sibling operation that also writes a Settlement's status and its splits together, already specifies this as "all together or not at all" with a dedicated "Failure changes nothing" scenario; `MarkReleased` should carry the same guarantee (backend#477).

## What Changes

- `Settlement.MarkReleased`'s requirement gains the same "all together or not at all" wording as `Order.CommitRefund`: the status flip, charge reference, released time and every split's payout reference are recorded together, or none of them are.
- A new scenario documents that a failure while recording any split leaves the Settlement, its charge reference/released time and every split exactly as they were (still Held, no partial payout references persisted).

## Capabilities

### Modified Capabilities

- `components/entity/settlement/mark-released`: the requirement is extended from "changes nothing" on the two known guard failures to "all together or not at all" for any failure during the operation, with a new scenario for a mid-operation failure.

## Impact

- **Code**: `backend/internal/infrastructure/database/rdb/settlement_repo.go` (`SettlementRepository.MarkReleased` wrapped in one pgx transaction, mirroring the existing `RefundRepository.CommitRefund` pattern) and its new integration test. No proto/RPC changes; no other entity or usecase spec depends on the split-write ordering.
