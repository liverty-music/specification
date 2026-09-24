# Organizer.SetZitadelOrgID

## Purpose

Records the sign-in tenant that provisioning created for an Organizer as its tenant link.

## Requirements

### Requirement: SetZitadelOrgID links one tenant to one Organizer

SetZitadelOrgID SHALL set the Organizer's tenant link to the given tenant, leaving its other attributes unchanged. Setting the link the Organizer already has SHALL succeed. It SHALL fail with NotFound when the Organizer does not exist, and with AlreadyExists when another Organizer is already linked to that tenant.

#### Scenario: Link is set

- **WHEN** the tenant is linked to no Organizer
- **THEN** the Organizer's tenant link becomes that tenant

#### Scenario: Same link again

- **WHEN** the Organizer is already linked to the same tenant
- **THEN** SetZitadelOrgID succeeds and nothing changes

#### Scenario: Tenant held by another Organizer

- **WHEN** another Organizer is already linked to the tenant
- **THEN** SetZitadelOrgID fails with AlreadyExists

#### Scenario: Unknown Organizer

- **WHEN** no Organizer has the id
- **THEN** SetZitadelOrgID fails with NotFound
