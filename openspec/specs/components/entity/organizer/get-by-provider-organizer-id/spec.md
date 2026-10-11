# Organizer.GetByProviderOrganizerID

## Purpose

Returns the Organizer whose provider organizer ID is the given sign-in tenant's ID, so an operator's own Organizer can be found from the tenant they signed in to.

## Requirements

### Requirement: GetByProviderOrganizerID returns the one Organizer linked to the tenant

GetByProviderOrganizerID SHALL return the Organizer whose provider organizer ID is the given one, in any status. At most one Organizer is linked to a tenant. It SHALL fail with NotFound when no Organizer is linked to the tenant, including while the Organizer meant for it is still provisioning and has no provider organizer ID.

#### Scenario: Linked tenant

- **WHEN** an Organizer's provider organizer ID is the given one
- **THEN** GetByProviderOrganizerID returns that Organizer

#### Scenario: Unlinked tenant

- **WHEN** no Organizer's provider organizer ID is the given one
- **THEN** GetByProviderOrganizerID fails with NotFound
