# components/adapter/organizer/api/rpc/reception-link Specification

## Purpose
The organizer-facing reception link service boundary: how an operator's sign-in is turned into their own Organizer before a ReceptionLink is issued, listed or revoked.

## Requirements

### Requirement: Every call acts for the caller's own active Organizer

Every call of the reception link service — Issue, List and Revoke — SHALL pass the same organizer-console sign-in checks as the organizer Organizer service, and SHALL then resolve the caller's own Organizer through OrganizerUseCase.ResolveCaller with the caller's tenant. A failure of ResolveCaller SHALL be returned unchanged and nothing else runs. The resolved Organizer SHALL be passed to ReceptionLinkUseCase.Issue, ListByEvent or Revoke; the request never names an Organizer.

#### Scenario: Operator issues a link

- **WHEN** an operator of an active Organizer calls Issue for their published event
- **THEN** the new link is returned

#### Scenario: Not signed in

- **WHEN** a request has no valid sign-in
- **THEN** it fails with Unauthenticated

#### Scenario: Deactivated Organizer

- **WHEN** the caller's Organizer is deactivated
- **THEN** every call fails with FailedPrecondition

### Requirement: Requests name what they act on

Issue SHALL fail with InvalidArgument, before any usecase runs, when the event is missing or malformed; List when the event is missing or malformed; Revoke when the link is missing or malformed.

#### Scenario: Issue without an event

- **WHEN** an operator calls Issue without an event
- **THEN** it fails with InvalidArgument and no link is created
