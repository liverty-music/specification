# Spec Delta

## Purpose

The organizer-facing Artist service boundary: an operator lists the Artists their own Organizer represents, and the Organizer is always the one the operator's sign-in resolves to.

## ADDED Requirements

### Requirement: Every artist call acts for the caller's own active Organizer

Every call of the organizer Artist service SHALL pass the same organizer-console sign-in checks as the organizer Organizer service, and SHALL then resolve the caller's own Organizer through OrganizerUseCase.ResolveCaller with the caller's tenant. A failure of ResolveCaller SHALL be returned unchanged and nothing is listed: PermissionDenied when no Organizer is linked to the tenant or the Organizer is provisioning, without revealing whether an Organizer exists, and FailedPrecondition when the Organizer is deactivated.

#### Scenario: Sign-in for another application

- **WHEN** an operator calls List with a sign-in that was not issued for the organizer console
- **THEN** it fails with PermissionDenied and nothing is listed

#### Scenario: Deactivated Organizer

- **WHEN** the caller's Organizer is deactivated
- **THEN** List fails with FailedPrecondition

### Requirement: List returns the caller's own roster

List SHALL take no input and SHALL return the result of OrganizerUseCase.ListOwnArtists for the caller's own Organizer, every represented Artist in one response; the request never names an Organizer, so an operator cannot ask for another Organizer's roster.

#### Scenario: Operator lists their own roster

- **WHEN** an operator calls List
- **THEN** it returns the Artists their Organizer represents, empty when it represents none
