## ADDED Requirements

### Requirement: Halmos symbolic proof of transfer immutability
Halmos SHALL prove that all ERC-721 transfer and approval functions revert for ALL possible inputs, not just fuzzed samples.

#### Scenario: transferFrom reverts for all inputs
- **WHEN** Halmos symbolically executes `transferFrom(from, to, tokenId)` for all possible `(from, to, tokenId)`
- **THEN** the execution MUST always revert

#### Scenario: safeTransferFrom reverts for all inputs
- **WHEN** Halmos symbolically executes both overloads of `safeTransferFrom` for all possible inputs
- **THEN** the execution MUST always revert

#### Scenario: approve reverts for all inputs
- **WHEN** Halmos symbolically executes `approve(spender, tokenId)` for all possible `(spender, tokenId)`
- **THEN** the execution MUST always revert

#### Scenario: setApprovalForAll reverts for all inputs
- **WHEN** Halmos symbolically executes `setApprovalForAll(operator, approved)` for all possible `(operator, approved)`
- **THEN** the execution MUST always revert

### Requirement: Halmos symbolic proof of access control
Halmos SHALL prove that only addresses with MINTER_ROLE can successfully call `mint`.

#### Scenario: Unauthorized mint reverts for all callers
- **WHEN** Halmos symbolically executes `mint(recipient, tokenId)` from any address without MINTER_ROLE
- **THEN** the execution MUST always revert

### Requirement: Halmos symbolic proof of locked status
Halmos SHALL prove that `locked()` returns `true` for every minted token.

#### Scenario: locked returns true for all minted tokens
- **WHEN** a token is minted and Halmos symbolically executes `locked(tokenId)`
- **THEN** the result MUST be `true`

### Requirement: Foundry invariant tests with Handler pattern
Foundry invariant tests SHALL verify that SBT invariants hold after any random sequence of contract operations.

#### Scenario: No token is ever transferred
- **WHEN** the fuzzer executes a random sequence of contract calls (mint, approve, transfer attempts)
- **THEN** `ownerOf(tokenId)` for every minted token MUST equal the original recipient

#### Scenario: Minted token count matches balanceOf sum
- **WHEN** the fuzzer executes a random sequence of mint operations
- **THEN** the total number of minted tokens MUST equal the sum of `balanceOf` across all recipients tracked by the Handler

#### Scenario: All minted tokens are locked
- **WHEN** the fuzzer executes a random sequence of contract calls
- **THEN** `locked(tokenId)` MUST return `true` for every minted token tracked by the Handler

### Requirement: Halmos CI integration
Halmos proofs SHALL run as a separate CI job on PRs targeting main.

#### Scenario: Halmos job runs on PR to main
- **WHEN** a PR targeting main modifies contract files
- **THEN** the `halmos` CI job MUST execute and all `check_` functions MUST pass

#### Scenario: Halmos failure blocks merge
- **WHEN** a Halmos proof fails (counterexample found)
- **THEN** the CI job MUST fail and block the PR from merging
