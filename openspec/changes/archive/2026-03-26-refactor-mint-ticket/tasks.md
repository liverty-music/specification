## 1. Extract validation sub-method

- [x] 1.1 Extract `validateMintParams(params *MintTicketParams) error` from `MintTicket` lines 80-98; move nil check, empty field checks, and ethAddressRe validation into the new private method
- [x] 1.2 Write table-driven unit tests for `validateMintParams` in `ticket_uc_test.go` covering all 5 scenarios from spec (nil params, empty eventID, empty userID, invalid address, valid params)

## 2. Extract idempotency check sub-method

- [x] 2.1 Extract `checkExistingTicket(ctx context.Context, eventID, userID string) (*entity.Ticket, bool, error)` from `MintTicket` lines 100-108; move DB lookup for existing ticket
- [x] 2.2 Write table-driven unit tests for `checkExistingTicket` in `ticket_uc_test.go` covering 3 scenarios (found, not found, DB error)

## 3. Extract mint-or-reconcile sub-method

- [x] 3.1 Extract `mintOrReconcile(ctx context.Context, params *MintTicketParams, tokenID uint64) (string, error)` from `MintTicket` lines 110-178; include token ID generation, on-chain existence check, owner verification, reconciliation, and fresh mint paths
- [x] 3.2 Write table-driven unit tests for `mintOrReconcile` in `ticket_uc_test.go` covering 4 scenarios (fresh mint, reconcile correct owner, reconcile wrong owner, on-chain check failure)

## 4. Extract persistence sub-method

- [x] 4.1 Extract `persistTicket(ctx context.Context, params *MintTicketParams, tokenID uint64, txHash string) (*entity.Ticket, error)` from `MintTicket` lines 180-202; move DB insert with concurrent conflict handling
- [x] 4.2 Write table-driven unit tests for `persistTicket` in `ticket_uc_test.go` covering 3 scenarios (successful insert, concurrent duplicate, DB write error)

## 5. Refactor MintTicket orchestrator

- [x] 5.1 Rewrite `MintTicket` as a ~30-line orchestrator that calls `validateMintParams`, `checkExistingTicket`, `mintOrReconcile`, `persistTicket` in sequence
- [x] 5.2 Verify all existing `MintTicket` tests pass without modification (regression safety net)
- [x] 5.3 Run `make check` to verify all lint and tests pass
