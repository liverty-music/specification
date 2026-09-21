# Create

## Purpose

The Organizer domain: the vetted seller an admin creates, its link to the
artists it represents, the runtime provisioning that gives each Organizer an
isolated Zitadel tenant its operator can sign into, and the admin surface to
manage them. The organizer-facing API and console are separate capabilities.

## Requirements

### Requirement: Admin creates an organizer with an initial operator

The system SHALL let an operator holding the platform `admin` role create an
Organizer with a name and an initial operator email. Creation is the vetting
— there is no separate `verified` flag and no self-serve registration. An
Organizer is distinct from an Artist and has its own OrganizerId. On success
the Organizer is provisioned an isolated Zitadel tenant (see idempotent
provisioning) with the initial operator seeded as its `owner`.

#### Scenario: Admin creates an organizer

- **WHEN** an operator with the `admin` role creates an Organizer with a name
  and an initial operator email
- **THEN** the Organizer SHALL exist with an isolated tenant and a `owner`
  operator, and SHALL become an active organizer

#### Scenario: Non-admin cannot create an organizer

- **WHEN** a create request is made without the `admin` role
- **THEN** the system SHALL reject it with a permission-denied error

#### Scenario: Organizer identity is separate from artist identity

- **WHEN** an artist self-publishes and an Organizer account is created for
  them
- **THEN** the Organizer SHALL have its own OrganizerId distinct from the
  Artist's ArtistId
