## Context

The backend follows Clean Architecture with entity, usecase, adapter, and infrastructure layers. The `MintTicket` method in `usecase/ticket_uc.go` (lines 79-203) is a 125-line function that interleaves three concerns: input validation, idempotency resolution with on-chain reconciliation, and database persistence. The on-chain reconciliation branch alone spans 20+ lines with nested conditionals checking token existence, owner matching, and PermissionDenied error paths.

The recent `enrich-entity-domain-logic` and `extract-entity-domain-logic` refactorings established the pattern of decomposing large functions into focused, testable units. This change applies the same principle within the usecase layer, where the logic depends on repository and minter interfaces and therefore stays in usecase rather than moving to entity.

## Goals / Non-Goals

**Goals:**
- Decompose `MintTicket` into 4 focused sub-methods: validation, idempotency check, mint-or-reconcile, and persistence
- Enable isolated unit testing of each sub-method (especially the reconciliation branch)
- Reduce `MintTicket` to a readable ~30-line orchestrator
- Use named structs for multi-return values instead of the 4-return anti-pattern seen in `resolveVenue`

**Non-Goals:**
- Changing any external behavior or RPC contract of `MintTicket`
- Moving logic to the entity layer (reconciliation depends on minter interface)
- Refactoring other methods in `ticket_uc.go`
- Adding new features or changing error codes

## Decisions

### 1. Sub-method visibility: private methods on `TicketUsecase`

**Decision**: All four extracted functions are private methods on `*TicketUsecase`, not package-level functions or standalone helpers.

**Rationale**: They access `TicketUsecase` dependencies (repository, minter, ethAddressRe regex). Making them methods keeps the dependency access natural without parameter bloat. They remain private because they are implementation details of `MintTicket`.

### 2. Return types: named structs over multi-value returns

**Decision**: `checkExistingTicket` returns `(*entity.Ticket, bool, error)` where the bool indicates "found". `mintOrReconcile` returns `(txHash string, err error)`.

**Rationale**: The `resolveVenue` pattern of returning 4 unnamed values is error-prone. For `checkExistingTicket`, a 3-return (entity, found-bool, error) follows the standard Go "comma ok" idiom. For `mintOrReconcile`, the output is a single txHash string, keeping the signature simple.

**Alternative considered**: A `mintResult` struct wrapping txHash. Rejected as over-engineering for a single string field.

### 3. validateMintParams stays in usecase layer

**Decision**: Keep `validateMintParams` as a private method on `*TicketUsecase` rather than moving validation to entity or to `MintTicketParams`.

**Rationale**: The validation uses `ethAddressRe` (a compiled regex on the usecase struct). Moving it to entity would require either passing the regex or duplicating it. The validation is specific to this use case's requirements, not a general entity invariant.

### 4. Reconciliation logic stays coupled

**Decision**: The on-chain reconciliation logic (check if minted, verify owner, return PermissionDenied on mismatch, use placeholder txHash for reconciled records) stays as a branch within `mintOrReconcile` rather than being extracted further.

**Rationale**: The reconciliation branch is a linear sequence of 3 steps that all share the same context (tokenID, recipient address). Extracting it into yet another sub-method would fragment a naturally cohesive flow. The `mintOrReconcile` method at ~40 lines is well within readable bounds.

### 5. Test strategy: sub-method unit tests + existing integration tests

**Decision**: Add focused unit tests for each sub-method. Keep existing `MintTicket` tests as integration-level tests that exercise the full orchestration.

**Rationale**: Sub-method tests can target specific edge cases (e.g., reconciliation with owner mismatch) without complex mock setup. The existing `MintTicket` tests validate end-to-end behavior is preserved.

## Risks / Trade-offs

- **[Risk] Behavioral drift during refactoring** → Mitigation: Existing `MintTicket` tests serve as regression safety net. No new behavior is added — only structural decomposition.
- **[Risk] Over-decomposition** → Mitigated by keeping reconciliation as a branch within `mintOrReconcile` rather than its own method. The 4-method decomposition matches the 3 natural responsibility boundaries + orchestrator.
- **[Trade-off] More methods = more indirection** → Accepted because each method has a clear single responsibility, and the orchestrator reads as a high-level summary. The total line count may increase slightly due to function signatures and doc comments.
