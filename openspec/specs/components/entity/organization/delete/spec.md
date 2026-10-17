# Organization.Delete

## Purpose
Removes an Organizer's Organization, with every identity in it.

## Requirements

### Requirement: Delete removes the Organization and its identities

Delete SHALL remove the given Organization and every identity in it, so none of the Organizer's members can sign in again. An Organization that no longer exists SHALL count as removed, so a repeated call succeeds. When the Organization cannot be removed it SHALL fail with Internal and the Organization stays.

#### Scenario: Organization with identities

- **WHEN** Delete runs for an Organization with one identity
- **THEN** the Organization and the identity no longer exist

#### Scenario: Already removed

- **WHEN** Delete runs for an Organization that no longer exists
- **THEN** it succeeds and nothing changes
