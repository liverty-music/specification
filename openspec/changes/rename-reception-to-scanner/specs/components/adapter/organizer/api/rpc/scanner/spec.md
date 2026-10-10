# Spec Delta

## Purpose

The organizer-facing scanner service boundary: how an operator's sign-in is turned into their own Organizer before a Scanner is created, listed or revoked.

## ADDED Requirements

### Requirement: Every call acts for the caller's own active Organizer

Every call of the organizer scanner service — Create, List and Revoke — SHALL pass the same organizer-console sign-in checks as the organizer Organizer service, and SHALL then resolve the caller's own Organizer through OrganizerUseCase.ResolveCaller with the caller's tenant. A failure of ResolveCaller SHALL be returned unchanged and nothing else runs. The resolved Organizer SHALL be passed to ScannerUseCase.Create, ListByEvent or Revoke; the request never names an Organizer.

#### Scenario: Operator creates a scanner

- **WHEN** an operator of an active Organizer calls Create for their published event
- **THEN** the new Scanner is returned

#### Scenario: Not signed in

- **WHEN** a request has no valid sign-in
- **THEN** it fails with Unauthenticated

#### Scenario: Deactivated Organizer

- **WHEN** the caller's Organizer is deactivated
- **THEN** every call fails with FailedPrecondition

### Requirement: Requests name what they act on

Create SHALL fail with InvalidArgument, before any usecase runs, when the event is missing or malformed; List when the event is missing or malformed; Revoke when the Scanner is missing or malformed.

#### Scenario: Create without an event

- **WHEN** an operator calls Create without an event
- **THEN** it fails with InvalidArgument and no Scanner is created
