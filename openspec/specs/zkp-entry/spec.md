# ZKP Entry

## Purpose

Defines the backend `EntryService` capability for zero-knowledge-proof-based event entry. `GetMerklePath` is a per-user RPC that returns the Merkle inclusion data (root, path elements, path indices, leaf) a fan needs to generate a Groth16 proof client-side; it carries an explicit `user_id` verified against the JWT-derived userID per the `rpc-auth-scoping` convention. `VerifyEntry` is unauthenticated by design — the zero-knowledge proof itself establishes ticket-holder membership without revealing the fan's identity, and nullifier uniqueness guards against replay. The capability deliberately splits these two roles: authenticated per-user read of path data, versus identity-free verification at venue entry.

## Requirements
### Requirement: GetMerklePath request carries explicit user_id

The `EntryService.GetMerklePath` RPC SHALL carry an explicit `entity.v1.UserId user_id` field in its request message. The field SHALL be marked required via `protovalidate`. The backend SHALL compare the supplied value against the userID derived from the JWT context and reject mismatches with `PERMISSION_DENIED` via the shared `requireMatchingUserID` helper defined by the `rpc-auth-scoping` capability.

#### Scenario: Matching user_id returns the caller's Merkle path

- **WHEN** an authenticated fan calls `GetMerklePath` with `user_id` equal to the JWT-derived userID and a valid `event_id` for which the fan holds a ticket
- **THEN** the handler SHALL return the Merkle root, path elements, path indices, and leaf needed to construct a client-side proof

#### Scenario: Mismatched user_id is rejected

- **WHEN** an authenticated fan calls `GetMerklePath` with `user_id` that differs from the JWT-derived userID
- **THEN** the handler SHALL return `PERMISSION_DENIED`
- **AND** no Merkle path data SHALL be returned
- **AND** the response SHALL NOT reveal whether the requested user holds a ticket for the event

#### Scenario: Missing user_id is rejected

- **WHEN** an authenticated fan calls `GetMerklePath` with an absent or empty `user_id`
- **THEN** the handler SHALL return `INVALID_ARGUMENT` via `protovalidate` enforcement

#### Scenario: Unauthenticated request is rejected before user_id check

- **WHEN** a client calls `GetMerklePath` without a valid JWT
- **THEN** the authentication middleware SHALL reject the request with `UNAUTHENTICATED` before the `user_id` check runs

---

### Requirement: VerifyEntry remains unauthenticated

The `EntryService.VerifyEntry` RPC SHALL remain unauthenticated and SHALL NOT carry a `user_id` field. The zero-knowledge proof itself establishes ticket-holder membership without revealing the fan's identity; the `rpc-auth-scoping` convention does not apply because there is no caller JWT to match against.

#### Scenario: VerifyEntry request shape

- **WHEN** a scanner device calls `VerifyEntry`
- **THEN** the request SHALL contain only `event_id`, `proof_json`, and `public_signals_json`
- **AND** the handler SHALL NOT require an `Authorization` header
- **AND** the handler SHALL NOT perform a JWT-userID vs request-userID comparison
- **AND** authorization SHALL be established entirely by the ZK proof plus the nullifier uniqueness check

