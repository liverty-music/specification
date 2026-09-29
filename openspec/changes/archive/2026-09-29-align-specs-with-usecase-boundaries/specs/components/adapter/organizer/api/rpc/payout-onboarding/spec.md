# Spec Delta

## MODIFIED Requirements

### Requirement: The caller must be an operator of their own active Organizer

Every request SHALL carry a valid sign-in, or fail with Unauthenticated. The sign-in SHALL be issued for the organizer console and grant organizer-console roles in exactly one tenant, or the request fails with PermissionDenied. The boundary SHALL resolve the caller's Organizer through OrganizerUseCase.ResolveCaller with that tenant and return its failure unchanged: PermissionDenied when no Organizer is linked or it is provisioning, without revealing whether an Organizer exists, and FailedPrecondition when it is deactivated.

#### Scenario: Not signed in

- **WHEN** a request has no valid sign-in
- **THEN** it fails with Unauthenticated

#### Scenario: Roles in several tenants

- **WHEN** the sign-in grants organizer-console roles in two tenants
- **THEN** it fails with PermissionDenied

#### Scenario: Tenant with no Organizer

- **WHEN** no Organizer is linked to the caller's tenant
- **THEN** it fails with PermissionDenied

#### Scenario: Deactivated Organizer

- **WHEN** the caller's Organizer is deactivated
- **THEN** it fails with FailedPrecondition
