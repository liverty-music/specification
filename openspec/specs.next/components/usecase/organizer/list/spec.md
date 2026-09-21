# List

## Purpose

The Organizer domain: the vetted seller an admin creates, its link to the
artists it represents, the runtime provisioning that gives each Organizer an
isolated Zitadel tenant its operator can sign into, and the admin surface to
manage them. The organizer-facing API and console are separate capabilities.

## Requirements

### Requirement: Admin lists and inspects organizers

The system SHALL provide admin-gated `List` and `Get` returning Organizers, and
`ListArtists` returning the artists an Organizer represents, so the admin
console can render the organizer-management screen.

#### Scenario: Admin lists organizers and inspects an organizer's artists

- **WHEN** an operator with the `admin` role lists organizers and then requests
  a given Organizer's artists
- **THEN** the system SHALL return the Organizers, and SHALL return the artists
  that Organizer represents

#### Scenario: Non-admin cannot list organizers

- **WHEN** a list/get request is made without the `admin` role
- **THEN** the system SHALL reject it with a permission-denied error
