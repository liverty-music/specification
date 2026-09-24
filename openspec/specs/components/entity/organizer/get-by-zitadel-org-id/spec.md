# Organizer.GetByZitadelOrgID

## Purpose

Returns the Organizer linked to a given sign-in tenant, so an operator's own Organizer can be found from the tenant they signed in to.

## Requirements

### Requirement: GetByZitadelOrgID returns the one Organizer linked to the tenant

GetByZitadelOrgID SHALL return the Organizer whose tenant link is the given tenant, in any status. At most one Organizer is linked to a tenant. It SHALL fail with NotFound when no Organizer is linked to the tenant, including while the Organizer meant for it is still provisioning and has no tenant link.

#### Scenario: Linked tenant

- **WHEN** an Organizer's tenant link is the given tenant
- **THEN** GetByZitadelOrgID returns that Organizer

#### Scenario: Unlinked tenant

- **WHEN** no Organizer's tenant link is the given tenant
- **THEN** GetByZitadelOrgID fails with NotFound
