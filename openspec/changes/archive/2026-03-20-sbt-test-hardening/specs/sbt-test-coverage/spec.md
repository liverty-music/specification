## ADDED Requirements

### Requirement: approve and setApprovalForAll MUST revert
TicketSBT SHALL override `approve` and `setApprovalForAll` to revert unconditionally. SBT tokens are non-transferable, so approval operations are semantically invalid and MUST be blocked at the contract level.

#### Scenario: approve reverts for any caller
- **WHEN** any address calls `approve(spender, tokenId)` on a minted token
- **THEN** the transaction MUST revert with message "SBT: Ticket transfer is prohibited"

#### Scenario: setApprovalForAll reverts for any caller
- **WHEN** any address calls `setApprovalForAll(operator, approved)`
- **THEN** the transaction MUST revert with message "SBT: Ticket transfer is prohibited"

### Requirement: All transfer paths MUST revert
All ERC-721 transfer functions SHALL revert unconditionally, including both overloads of `safeTransferFrom`.

#### Scenario: 3-argument safeTransferFrom reverts
- **WHEN** token owner calls `safeTransferFrom(from, to, tokenId)` (3-argument version)
- **THEN** the transaction MUST revert with message "SBT: Ticket transfer is prohibited"

#### Scenario: 4-argument safeTransferFrom reverts
- **WHEN** token owner calls `safeTransferFrom(from, to, tokenId, data)` (4-argument version)
- **THEN** the transaction MUST revert with message "SBT: Ticket transfer is prohibited"

#### Scenario: transferFrom reverts
- **WHEN** token owner calls `transferFrom(from, to, tokenId)`
- **THEN** the transaction MUST revert with message "SBT: Ticket transfer is prohibited"

### Requirement: Duplicate mint MUST revert
The contract SHALL revert when attempting to mint a token with an already-used tokenId.

#### Scenario: Minting with existing tokenId fails
- **WHEN** minter calls `mint(recipient, tokenId)` with a tokenId that has already been minted
- **THEN** the transaction MUST revert

### Requirement: Mint to zero address MUST revert
The contract SHALL revert when attempting to mint a token to `address(0)`.

#### Scenario: Minting to address(0) fails
- **WHEN** minter calls `mint(address(0), tokenId)`
- **THEN** the transaction MUST revert

### Requirement: ERC-165 supportsInterface correctness
The contract SHALL correctly report support for ERC-721, ERC-5192, and AccessControl interfaces via `supportsInterface`.

#### Scenario: Reports ERC-721 support
- **WHEN** `supportsInterface` is called with ERC-721 interfaceId (`0x80ac58cd`)
- **THEN** it MUST return `true`

#### Scenario: Reports ERC-5192 support
- **WHEN** `supportsInterface` is called with ERC-5192 interfaceId
- **THEN** it MUST return `true`

#### Scenario: Reports AccessControl support
- **WHEN** `supportsInterface` is called with IAccessControl interfaceId
- **THEN** it MUST return `true`

#### Scenario: Returns false for unsupported interface
- **WHEN** `supportsInterface` is called with an unsupported interfaceId (`0xffffffff`)
- **THEN** it MUST return `false`

### Requirement: AccessControl role management
Admin SHALL be able to grant and revoke MINTER_ROLE. Non-admin addresses SHALL NOT be able to grant roles. A revoked minter SHALL NOT be able to mint.

#### Scenario: Admin grants MINTER_ROLE
- **WHEN** admin calls `grantRole(MINTER_ROLE, newMinter)`
- **THEN** `hasRole(MINTER_ROLE, newMinter)` MUST return `true`

#### Scenario: Admin revokes MINTER_ROLE
- **WHEN** admin calls `revokeRole(MINTER_ROLE, minter)`
- **THEN** `hasRole(MINTER_ROLE, minter)` MUST return `false`

#### Scenario: Revoked minter cannot mint
- **WHEN** admin revokes MINTER_ROLE from minter, and the former minter calls `mint(recipient, tokenId)`
- **THEN** the transaction MUST revert

#### Scenario: Non-admin cannot grant roles
- **WHEN** a non-admin address calls `grantRole(MINTER_ROLE, other)`
- **THEN** the transaction MUST revert

### Requirement: Constructor initializes correct state
The contract SHALL set name, symbol, and roles correctly at deployment.

#### Scenario: Name and symbol are correct
- **WHEN** the contract is deployed
- **THEN** `name()` MUST return "Liverty Music Ticket" and `symbol()` MUST return "LMTKT"

#### Scenario: Admin has both roles
- **WHEN** the contract is deployed with `admin` address
- **THEN** `hasRole(DEFAULT_ADMIN_ROLE, admin)` and `hasRole(MINTER_ROLE, admin)` MUST both return `true`

### Requirement: Fuzz testing for mint and access control
The contract SHALL be tested with fuzz inputs to verify robustness against arbitrary tokenIds, recipient addresses, and unauthorized callers.

#### Scenario: Fuzz mint with arbitrary tokenId
- **WHEN** minter calls `mint(recipient, tokenId)` with any valid `uint256 tokenId` and non-zero `recipient`
- **THEN** `ownerOf(tokenId)` MUST return `recipient`

#### Scenario: Fuzz unauthorized mint with arbitrary caller
- **WHEN** an arbitrary address without MINTER_ROLE calls `mint(recipient, tokenId)`
- **THEN** the transaction MUST revert
