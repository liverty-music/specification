# Capability: Ticket Minting Internals

## Purpose

Defines the internal sub-method structure of the `MintTicket` operation. The public `MintTicket` method acts as a pure orchestrator; each sub-method owns a single concern (validation, idempotency check, on-chain interaction, persistence).

## Requirements

### Requirement: MintTicket orchestrator conciseness

The `MintTicket` public method SHALL serve as a pure orchestrator that delegates to sub-methods. It SHALL NOT contain inline validation logic, database queries, or on-chain interaction code.

#### Scenario: Orchestrator line count

- **WHEN** `MintTicket` is measured after refactoring
- **THEN** the method body (excluding signature and doc comment) is 30 lines or fewer

#### Scenario: Orchestrator delegates all concerns

- **WHEN** reading `MintTicket` source code
- **THEN** it contains exactly 4 sub-method calls: `validateMintParams`, `checkExistingTicket`, `mintOrReconcile`, `persistTicket`

---

### Requirement: Input validation isolation

The `validateMintParams` method SHALL validate all input fields and return an `InvalidArgument` error on failure. It SHALL be a pure validation function with no side effects (no DB calls, no on-chain calls).

#### Scenario: Nil params

- **WHEN** params is nil
- **THEN** returns InvalidArgument error

#### Scenario: Empty event ID

- **WHEN** params has empty EventID
- **THEN** returns InvalidArgument error mentioning event ID

#### Scenario: Empty user ID

- **WHEN** params has empty UserID
- **THEN** returns InvalidArgument error mentioning user ID

#### Scenario: Invalid Ethereum address

- **WHEN** params has RecipientAddress that does not match `^0x[0-9a-fA-F]{40}$`
- **THEN** returns InvalidArgument error mentioning Ethereum address

#### Scenario: Valid params

- **WHEN** all fields are non-empty and RecipientAddress matches the regex
- **THEN** returns nil

---

### Requirement: Idempotency check isolation

The `checkExistingTicket` method SHALL query the database for an existing ticket by event ID and user ID. It SHALL return the existing ticket when found, or indicate absence when not found.

#### Scenario: Ticket exists in database

- **WHEN** a ticket with matching eventID and userID exists in the database
- **THEN** returns the existing ticket entity and found=true

#### Scenario: Ticket does not exist

- **WHEN** no ticket with matching eventID and userID exists
- **THEN** returns nil ticket and found=false

#### Scenario: Database error propagation

- **WHEN** the database query fails with a transient error
- **THEN** returns the error without wrapping it as a business error

---

### Requirement: Mint-or-reconcile isolation

The `mintOrReconcile` method SHALL handle both fresh minting and on-chain reconciliation. It SHALL generate a token ID, check on-chain state, and either mint a new token or reconcile an existing one.

#### Scenario: Fresh mint (token not on chain)

- **WHEN** token ID is not yet minted on-chain
- **THEN** calls minter.Mint and returns the resulting txHash

#### Scenario: Reconcile existing token with correct owner

- **WHEN** token ID already exists on-chain AND the owner matches the expected recipient
- **THEN** returns a placeholder txHash without calling minter.Mint

#### Scenario: Reconcile existing token with wrong owner

- **WHEN** token ID already exists on-chain AND the owner does NOT match the expected recipient
- **THEN** returns a PermissionDenied error

#### Scenario: On-chain check failure

- **WHEN** the on-chain existence check fails
- **THEN** returns the error to the caller

---

### Requirement: Persistence isolation

The `persistTicket` method SHALL insert the ticket into the database and handle concurrent duplicate conflicts gracefully.

#### Scenario: Successful insert

- **WHEN** no conflicting ticket exists
- **THEN** inserts the ticket and returns nil error

#### Scenario: Concurrent duplicate

- **WHEN** another request inserted a ticket with the same event ID and user ID concurrently
- **THEN** returns the already-existing ticket instead of an error (idempotent behavior)

#### Scenario: Database write error

- **WHEN** the database insert fails with a non-conflict error
- **THEN** returns the error to the caller

---

### Requirement: No multi-value return anti-pattern

Sub-methods SHALL NOT return more than 3 values. When a method needs to communicate multiple pieces of data, it SHALL use a named struct or the standard Go "comma ok" idiom.

#### Scenario: checkExistingTicket return signature

- **WHEN** inspecting the `checkExistingTicket` method signature
- **THEN** it returns at most 3 values: `(*entity.Ticket, bool, error)`

#### Scenario: mintOrReconcile return signature

- **WHEN** inspecting the `mintOrReconcile` method signature
- **THEN** it returns at most 2 values: `(string, error)`
