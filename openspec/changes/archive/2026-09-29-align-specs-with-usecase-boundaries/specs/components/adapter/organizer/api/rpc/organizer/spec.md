# Spec Delta

## MODIFIED Requirements

### Requirement: Only the caller's own active Organizer is served

The boundary SHALL resolve the caller's own Organizer through OrganizerUseCase.ResolveCaller with the caller's tenant and serve the request only for the Organizer it returns. A failure of ResolveCaller SHALL be returned unchanged and nothing else runs: PermissionDenied when no Organizer is linked to the tenant or the Organizer is provisioning, without revealing whether an Organizer exists, and FailedPrecondition when the Organizer is deactivated.

#### Scenario: Tenant with no Organizer

- **WHEN** no Organizer is linked to the caller's tenant
- **THEN** the request fails with PermissionDenied and does not reveal whether an Organizer exists

#### Scenario: Provisioning Organizer

- **WHEN** the caller's Organizer is provisioning
- **THEN** the request fails with PermissionDenied

#### Scenario: Deactivated Organizer

- **WHEN** the caller's Organizer is deactivated
- **THEN** the request fails with FailedPrecondition

### Requirement: ListArtists lists only the caller's own roster

ListArtists SHALL require an OrganizerId, failing with InvalidArgument when it is missing or malformed. It SHALL return the result of OrganizerUseCase.ListOwnArtists for the caller's own Organizer and the requested OrganizerId, every represented Artist in one response; when the OrganizerId is not the caller's own Organizer's id, ListOwnArtists fails with PermissionDenied and nothing is listed.

#### Scenario: Operator lists their own roster

- **WHEN** an operator calls ListArtists with their own Organizer's id
- **THEN** it returns the Artists that Organizer represents, empty when it represents none

#### Scenario: Another Organizer's roster

- **WHEN** an operator calls ListArtists with an OrganizerId that is not their own Organizer's
- **THEN** it fails with PermissionDenied

#### Scenario: Missing or malformed OrganizerId

- **WHEN** ListArtists is called without an OrganizerId or with a malformed one
- **THEN** it fails with InvalidArgument
