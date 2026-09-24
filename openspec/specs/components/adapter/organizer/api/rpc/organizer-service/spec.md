# Organizer OrganizerService RPC

## Purpose

The organizer-facing Organizer service boundary: how an operator's sign-in is turned into their own Organizer, and what the boundary decides before OrganizerUseCase runs for Get and ListArtists.

## Requirements

### Requirement: The caller's tenant comes from their organizer-console sign-in

Every request SHALL carry a valid sign-in, or fail with Unauthenticated. The sign-in SHALL be issued for the organizer console, or the request fails with PermissionDenied. The caller's tenant SHALL be the single tenant in which the sign-in grants the operator any organizer-console role; any role is enough. A sign-in that grants roles in no tenant, or in more than one, SHALL fail with PermissionDenied. These checks come before the request's fields are validated, and a request that fails them has no effect.

#### Scenario: Not signed in

- **WHEN** a request has no valid sign-in
- **THEN** it fails with Unauthenticated

#### Scenario: Sign-in for another application

- **WHEN** the sign-in was not issued for the organizer console
- **THEN** it fails with PermissionDenied

#### Scenario: No role in any tenant

- **WHEN** the sign-in grants no organizer-console role
- **THEN** it fails with PermissionDenied

#### Scenario: Roles in several tenants

- **WHEN** the sign-in grants organizer-console roles in two tenants
- **THEN** it fails with PermissionDenied

### Requirement: Only the caller's own active Organizer is served

The boundary SHALL resolve the caller's own Organizer through OrganizerUseCase.GetByZitadelOrgID with the caller's tenant, and serve the request only when that Organizer serves its operators. When no Organizer is linked to the tenant, or the Organizer is provisioning, the request SHALL fail with PermissionDenied without revealing whether an Organizer exists. When the Organizer is deactivated, the request SHALL fail with FailedPrecondition and may say that the Organizer is deactivated, since it is the caller's own.

#### Scenario: Tenant with no Organizer

- **WHEN** no Organizer is linked to the caller's tenant
- **THEN** the request fails with PermissionDenied and does not reveal whether an Organizer exists

#### Scenario: Provisioning Organizer

- **WHEN** the caller's Organizer is provisioning
- **THEN** the request fails with PermissionDenied

#### Scenario: Deactivated Organizer

- **WHEN** the caller's Organizer is deactivated
- **THEN** the request fails with FailedPrecondition

### Requirement: Get returns the caller's own Organizer

Get SHALL take no input and SHALL return the caller's own Organizer's id and name. It is how the organizer console first learns its OrganizerId. It does not return the roster.

#### Scenario: Operator reads their own Organizer

- **WHEN** an operator of an active Organizer calls Get
- **THEN** it returns that Organizer's id and name

### Requirement: ListArtists lists only the caller's own roster

ListArtists SHALL require an OrganizerId, failing with InvalidArgument when it is missing or malformed. The OrganizerId SHALL be the caller's own Organizer's id, or the request fails with PermissionDenied and nothing is listed. It SHALL return the result of OrganizerUseCase.ListArtists for that Organizer, every represented Artist in one response.

#### Scenario: Operator lists their own roster

- **WHEN** an operator calls ListArtists with their own Organizer's id
- **THEN** it returns the Artists that Organizer represents, empty when it represents none

#### Scenario: Another Organizer's roster

- **WHEN** an operator calls ListArtists with an OrganizerId that is not their own Organizer's
- **THEN** it fails with PermissionDenied

#### Scenario: Missing or malformed OrganizerId

- **WHEN** ListArtists is called without an OrganizerId or with a malformed one
- **THEN** it fails with InvalidArgument
