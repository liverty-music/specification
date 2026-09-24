# Organizer Concert RPC

## Purpose

The organizer-facing concert service boundary: how an operator's sign-in is turned into their own Organizer before any authoring call runs, and which drafts the boundary rejects before the usecase sees them.

## Requirements

### Requirement: Every authoring call acts for the caller's own active Organizer

Every call of the organizer concert service — Create, Update, Publish, Cancel, List, RegenerateToken, CreateMediaUploadURL and AttachMedia — SHALL pass the same organizer-console sign-in checks as the organizer Organizer service, and SHALL then resolve the caller's own Organizer through OrganizerUseCase.GetByZitadelOrgID with the caller's tenant. When no Organizer is linked to the tenant, or the Organizer is provisioning, the call SHALL fail with PermissionDenied without revealing whether an Organizer exists. When the Organizer is deactivated, the call SHALL fail with FailedPrecondition. Ownership of the Series named in a request is checked by the usecase, not here.

#### Scenario: Operator of an active Organizer lists concerts

- **WHEN** an operator of an active Organizer calls List
- **THEN** the Organizer's own concerts are returned

#### Scenario: Provisioning Organizer

- **WHEN** the caller's Organizer is provisioning
- **THEN** every authoring call fails with PermissionDenied and nothing is stored

#### Scenario: Deactivated Organizer

- **WHEN** the caller's Organizer is deactivated
- **THEN** every authoring call fails with FailedPrecondition

### Requirement: A draft names at least one performer and one event

Create and Update SHALL fail with InvalidArgument, before any usecase runs, when the draft names no Artist or no event.

#### Scenario: Draft without events

- **WHEN** an operator calls Create with a draft that has a performer and no event
- **THEN** it fails with InvalidArgument and no Series is created

### Requirement: RegenerateToken returns the new token

RegenerateToken SHALL return the Series' new unlisted share token; the organizer console builds the share link from it.

#### Scenario: New token

- **WHEN** an operator regenerates the token of their UNLISTED Series
- **THEN** the response carries the new token and the old share link stops working
