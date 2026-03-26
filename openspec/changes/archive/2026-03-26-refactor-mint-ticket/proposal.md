## Why

The `MintTicket` method in `ticket_uc.go` (lines 79-203, 125 lines) handles three distinct responsibilities in a single function: input validation, idempotency resolution with on-chain reconciliation, and database persistence with concurrent conflict handling. This makes it difficult to test individual concerns in isolation — every test requires mocking the full dependency graph (repository, minter, token ID generator) even when testing pure validation logic. The on-chain reconciliation branch (checking if a token already exists, verifying owner, returning PermissionDenied on mismatch) is particularly complex and buried inside the larger method, making it hard to reason about and verify independently.

## What Changes

- **Extract `validateMintParams`**: Move nil check, empty field checks, and Ethereum address regex validation into a private method. This is a pure function that can be tested without any mocks.
- **Extract `checkExistingTicket`**: Move the DB idempotency lookup (existing ticket check by eventID + userID) into a private method returning a structured result.
- **Extract `mintOrReconcile`**: Move the on-chain logic — token ID generation, on-chain existence check, owner verification, reconciliation vs fresh mint — into a private method. This isolates the most complex branching logic.
- **Extract `persistTicket`**: Move the DB insert with concurrent conflict handling (duplicate key detection) into a private method.
- **Slim `MintTicket` to orchestrator**: Reduce the public method to ~30 lines that call the four sub-methods in sequence, making the high-level flow immediately readable.

## Capabilities

### New Capabilities

- `ticket-minting-internals`: Covers internal quality requirements for the ticket minting decomposition — sub-method responsibilities, testability, and structural constraints.

### Modified Capabilities

(none — no spec-level behavior changes; this is an internal restructuring)

## Impact

- **`internal/usecase/ticket_uc.go`**: `MintTicket` refactored from 125 lines to ~30 lines orchestrator + 4 private sub-methods. No signature changes to the public method.
- **`internal/usecase/ticket_uc_test.go`**: New unit tests for each sub-method. Existing `MintTicket` integration tests remain unchanged.
- **No API changes**: No proto, RPC, or database changes. The `MintTicket` RPC handler and its public signature are unchanged.
- **No migration needed**: No schema or infrastructure impact.
