# OrganizerConnectedAccount.GetByOrganizerID

## Purpose

Returns the connected account stored for an Organizer.

## Requirements

### Requirement: GetByOrganizerID returns the Organizer's account

GetByOrganizerID SHALL return the Organizer's stored account with its account reference and last stored status, and SHALL fail with NotFound when the Organizer has no stored account.

#### Scenario: Stored account

- **WHEN** the Organizer has a stored account
- **THEN** GetByOrganizerID returns it

#### Scenario: No account

- **WHEN** the Organizer has no stored account
- **THEN** GetByOrganizerID fails with NotFound
