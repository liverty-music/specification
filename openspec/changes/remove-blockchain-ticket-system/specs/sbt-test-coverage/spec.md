## REMOVED Requirements

### Requirement: approve and setApprovalForAll MUST revert
**Reason**: The `TicketSBT` Solidity contract and its Foundry test suite are removed under the Scenario A pivot; there is no on-chain token.
**Migration**: None; `contracts/` is deleted.

### Requirement: All transfer paths MUST revert
**Reason**: `TicketSBT` contract removed.
**Migration**: None; `contracts/` is deleted.

### Requirement: Duplicate mint MUST revert
**Reason**: `TicketSBT` contract removed.
**Migration**: None; `contracts/` is deleted.

### Requirement: Mint to zero address MUST revert
**Reason**: `TicketSBT` contract removed.
**Migration**: None; `contracts/` is deleted.

### Requirement: ERC-165 supportsInterface correctness
**Reason**: `TicketSBT` contract removed.
**Migration**: None; `contracts/` is deleted.

### Requirement: AccessControl role management
**Reason**: `TicketSBT` contract removed (no `MINTER_ROLE`).
**Migration**: None; `contracts/` is deleted.

### Requirement: Constructor initializes correct state
**Reason**: `TicketSBT` contract removed.
**Migration**: None; `contracts/` is deleted.

### Requirement: Fuzz testing for mint and access control
**Reason**: `TicketSBT` contract removed.
**Migration**: None; `contracts/` is deleted.
