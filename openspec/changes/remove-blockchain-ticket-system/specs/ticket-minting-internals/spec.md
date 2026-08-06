## REMOVED Requirements

### Requirement: MintTicket orchestrator conciseness
**Reason**: The `MintTicket` on-chain operation is removed with the blockchain ticket stack under the Scenario A pivot.
**Migration**: No live consumer. Web2 issuance internals, if needed, will be specified by the follow-up Web2 ticket change.

### Requirement: Input validation isolation
**Reason**: Sub-method of the removed on-chain `MintTicket` operation.
**Migration**: None; code deleted.

### Requirement: Idempotency check isolation
**Reason**: Sub-method of the removed on-chain `MintTicket` operation.
**Migration**: None; code deleted.

### Requirement: Mint-or-reconcile isolation
**Reason**: Sub-method of the removed on-chain `MintTicket` operation (on-chain reconciliation is gone).
**Migration**: None; code deleted.

### Requirement: Persistence isolation
**Reason**: Sub-method of the removed on-chain `MintTicket` operation.
**Migration**: None; code deleted.

### Requirement: No multi-value return anti-pattern
**Reason**: Structural rule scoped to the removed `MintTicket` sub-methods.
**Migration**: None; code deleted.
