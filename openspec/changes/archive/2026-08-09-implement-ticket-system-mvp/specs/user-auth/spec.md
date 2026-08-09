## ADDED Requirements

### Requirement: Passkey Authentication via Zitadel
The system SHALL use Zitadel (existing IdP) as the WebAuthn Relying Party for Passkey registration and authentication. For MVP, Zitadel's hosted login UI handles the WebAuthn ceremony.

#### Scenario: Passkey Registration
- **WHEN** a user initiates Passkey registration
- **THEN** Zitadel's hosted login UI SHALL prompt the user to create a Passkey
- **AND** Zitadel SHALL store the credential internally

#### Scenario: Passkey Authentication
- **WHEN** a user authenticates via Passkey
- **THEN** Zitadel's hosted login UI SHALL handle the WebAuthn assertion
- **AND** issue a JWT via the existing OIDC flow (`oidc-client-ts`)

### Requirement: Smart Account Mapping
The system SHALL deterministically map a user's internal ID to a Smart Account (Safe) address.

#### Scenario: Safe Address Derivation
- **WHEN** a user is associated with a ticket operation
- **THEN** a predicted Safe (ERC-4337) address SHALL be derived from `users.id` (UUIDv7) using `CREATE2(salt = keccak256(users.id))`
- **AND** this derivation SHALL be auth-provider-agnostic (independent of Zitadel or credential material)

### Requirement: Auth-Agnostic Identification
All ticket system data SHALL reference `users.id` (internal UUIDv7) as the user identifier, never `users.external_id` (Zitadel sub claim) or credential-specific values.

#### Scenario: Foreign Key References
- **WHEN** a new ticket, nullifier, or Merkle tree entry is created
- **THEN** the user reference SHALL be `users.id`
- **AND** the system SHALL remain functional if the authentication provider changes
