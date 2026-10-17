# Organizer.GetByProviderOrganizerID

## Purpose

Returns the Organizer whose provider organizer ID is the given Organization's ID, so a member's own Organizer can be found from the Organization they signed in to.

## Requirements

### Requirement: GetByProviderOrganizerID returns the one Organizer linked to the Organization

GetByProviderOrganizerID SHALL return the Organizer whose provider organizer ID is the given one, in any status. At most one Organizer is linked to an Organization. It SHALL fail with NotFound when no Organizer is linked to the Organization, including while the Organizer meant for it is still provisioning and has no provider organizer ID.

#### Scenario: Linked Organization

- **WHEN** an Organizer's provider organizer ID is the given one
- **THEN** GetByProviderOrganizerID returns that Organizer

#### Scenario: Unlinked Organization

- **WHEN** no Organizer's provider organizer ID is the given one
- **THEN** GetByProviderOrganizerID fails with NotFound
