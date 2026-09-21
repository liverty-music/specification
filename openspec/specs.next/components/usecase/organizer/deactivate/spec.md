# Deactivate

## Purpose

The Organizer domain: the vetted seller an admin creates, its link to the
artists it represents, the runtime provisioning that gives each Organizer an
isolated Zitadel tenant its operator can sign into, and the admin surface to
manage them. The organizer-facing API and console are separate capabilities.

## Requirements

### Requirement: An organizer can be deactivated

The system SHALL support deactivating an Organizer. For a deactivated
Organizer, the backend SHALL reject all organizer operations, its operators
SHALL be deactivated in Zitadel, and its artist associations SHALL be freed
so the artists can be re-associated. Full teardown of the tenant org and
grants is out of scope for this change.

#### Scenario: Deactivated organizer's operations are rejected

- **WHEN** an Organizer is deactivated and a request targets it
- **THEN** the system SHALL reject the request and the Organizer's operators
  SHALL no longer be able to act

#### Scenario: Deactivation frees the organizer's artists

- **WHEN** an Organizer with associated artists is deactivated
- **THEN** those artists SHALL become associable to another Organizer
