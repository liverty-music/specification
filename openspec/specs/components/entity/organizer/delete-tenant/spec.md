# components/entity/organizer/delete-tenant Specification

## Purpose
Organizer.DeleteTenant removes an Organizer's isolated sign-in tenant, with every operator in it.

## Requirements

### Requirement: DeleteTenant removes the tenant and its operators

DeleteTenant SHALL remove the given tenant and every operator in it, so none of them can sign in again. A tenant that no longer exists SHALL count as removed, so a repeated call succeeds. When the tenant cannot be removed it SHALL fail with Internal and the tenant stays.

#### Scenario: Tenant with operators

- **WHEN** DeleteTenant runs for a tenant with one operator
- **THEN** the tenant and the operator no longer exist

#### Scenario: Already removed

- **WHEN** DeleteTenant runs for a tenant that no longer exists
- **THEN** it succeeds and nothing changes
