# OrganizerUseCase.GetByZitadelOrgID

## Purpose

OrganizerUseCase.GetByZitadelOrgID returns the Organizer linked to a given sign-in tenant, so an operator's own Organizer can be found from the tenant they signed in to.

## Requirements

### Requirement: GetByZitadelOrgID returns the Organizer linked to the tenant

GetByZitadelOrgID SHALL return the Organizer through Organizer.GetByZitadelOrgID, whatever its status, and SHALL fail with NotFound when no Organizer is linked to the tenant. Whether the Organizer may serve the caller is decided by the caller from its status.

#### Scenario: Linked tenant

- **WHEN** an Organizer is linked to the tenant
- **THEN** GetByZitadelOrgID returns it with its status

#### Scenario: Unlinked tenant

- **WHEN** no Organizer is linked to the tenant
- **THEN** GetByZitadelOrgID fails with NotFound
