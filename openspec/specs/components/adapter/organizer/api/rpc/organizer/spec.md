# Organizer OrganizerService RPC

## Purpose

The organizer-facing Organizer service boundary: how a member's sign-in is turned into their own Organizer, and what the boundary decides before OrganizerUseCase runs for Get.

## Requirements

### Requirement: The caller's Organization comes from their organizer-console sign-in

Every request SHALL carry a valid sign-in, or fail with Unauthenticated. The sign-in SHALL be issued for the organizer console, or the request fails with PermissionDenied. The caller's Organization SHALL be the single Organization in which the sign-in grants the member any organizer-console role; any role is enough. A sign-in that grants roles in no Organization, or in more than one, SHALL fail with PermissionDenied. These checks come before the request's fields are validated, and a request that fails them has no effect.

#### Scenario: Not signed in

- **WHEN** a request has no valid sign-in
- **THEN** it fails with Unauthenticated

#### Scenario: Sign-in for another application

- **WHEN** the sign-in was not issued for the organizer console
- **THEN** it fails with PermissionDenied

#### Scenario: No role in any Organization

- **WHEN** the sign-in grants no organizer-console role
- **THEN** it fails with PermissionDenied

#### Scenario: Roles in several Organizations

- **WHEN** the sign-in grants organizer-console roles in two Organizations
- **THEN** it fails with PermissionDenied

### Requirement: Only the caller's own active Organizer is served

The boundary SHALL resolve the caller's own Organizer through OrganizerUseCase.ResolveCaller with the caller's Organization and serve the request only for the Organizer it returns. A failure of ResolveCaller SHALL be returned unchanged and nothing else runs: PermissionDenied when no Organizer is linked to the Organization or the Organizer is provisioning, without revealing whether an Organizer exists, and FailedPrecondition when the Organizer is deactivated.

#### Scenario: Organization with no Organizer

- **WHEN** no Organizer is linked to the caller's Organization
- **THEN** the request fails with PermissionDenied and does not reveal whether an Organizer exists

#### Scenario: Provisioning Organizer

- **WHEN** the caller's Organizer is provisioning
- **THEN** the request fails with PermissionDenied

#### Scenario: Deactivated Organizer

- **WHEN** the caller's Organizer is deactivated
- **THEN** the request fails with FailedPrecondition

### Requirement: Get returns the caller's own Organizer

Get SHALL take no input and SHALL return the caller's own Organizer's id and name. It is how the organizer console first learns its OrganizerId. It does not return the roster.

#### Scenario: Member reads their own Organizer

- **WHEN** a member of an active Organizer calls Get
- **THEN** it returns that Organizer's id and name

### Requirement: SendSignInLinks needs no sign-in and reveals nothing

SendSignInLinks SHALL be callable without a sign-in. It SHALL take an email address, fail with InvalidArgument when it is missing or not an email address, and run OrganizerUseCase.SendSignInLinks with it, identifying the client for the per-client limit by its network address. It SHALL answer with an empty success whenever the usecase succeeds, whether or not any Organizer has the address, and SHALL return ResourceExhausted unchanged. It is the only call of the organizer Organizer service that needs no sign-in.

#### Scenario: Owner asks for sign-in links

- **WHEN** SendSignInLinks is called without a sign-in for the owner email of an active Organizer
- **THEN** it succeeds with an empty response and the owner receives the links

#### Scenario: Unknown address

- **WHEN** SendSignInLinks is called for an address that owns no Organizer
- **THEN** it succeeds with the same empty response

#### Scenario: Malformed address

- **WHEN** SendSignInLinks is called with `band@`
- **THEN** it fails with InvalidArgument

#### Scenario: Too many requests

- **WHEN** the client exceeded the per-client limit
- **THEN** it fails with ResourceExhausted
