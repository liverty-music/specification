## MODIFIED Requirements

### Requirement: External Identity Mapping

The system SHALL maintain a unique mapping between Zitadel identity (`sub` claim) and the local user record using a TEXT-typed `external_id` column. The column accepts any string format to accommodate identity provider ID schemes (e.g., Zitadel snowflake IDs, UUIDs).

#### Scenario: Store external identity

- **WHEN** a new user record is created via `Create`
- **THEN** the `external_id` column SHALL be set to the Zitadel `sub` claim value as a plain string
- **AND** the `external_id` column SHALL have a UNIQUE constraint

#### Scenario: Lookup by external identity

- **WHEN** the system receives a request with a Zitadel `sub` claim
- **THEN** the system SHALL be able to find the corresponding local user by `external_id`

### Requirement: User Entity External ID Field

The `User` protobuf entity SHALL include an `external_id` field to represent the Zitadel identity link.

#### Scenario: External ID in User entity

- **WHEN** a `User` entity is serialized
- **THEN** it SHALL include the `external_id` field as a non-empty string
- **AND** the field SHALL be validated as a non-empty string via protovalidate (not UUID format)
