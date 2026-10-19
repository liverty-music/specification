# Organizer PayoutAccountService RPC

## Purpose

The organizer-facing payout account boundary: it resolves the caller's own Organizer from their sign-in and returns that Organizer's payout-receiving account through PayoutAccountUseCase.Get, or starts its onboarding at the payment provider through PayoutAccountUseCase.StartOnboarding.

## Requirements

### Requirement: The caller must be a member of their own active Organizer

Every request SHALL carry a valid sign-in, or fail with Unauthenticated. The sign-in SHALL be issued for the organizer console and grant organizer-console roles in exactly one Organization, or the request fails with PermissionDenied. The boundary SHALL resolve the caller's Organizer through OrganizerUseCase.ResolveCaller with that Organization and return its failure unchanged: PermissionDenied when no Organizer is linked or it is provisioning, without revealing whether an Organizer exists, and FailedPrecondition when it is deactivated.

#### Scenario: Not signed in

- **WHEN** a request has no valid sign-in
- **THEN** it fails with Unauthenticated

#### Scenario: Roles in several Organizations

- **WHEN** the sign-in grants organizer-console roles in two Organizations
- **THEN** it fails with PermissionDenied

#### Scenario: Organization with no Organizer

- **WHEN** no Organizer is linked to the caller's Organization
- **THEN** it fails with PermissionDenied

#### Scenario: Deactivated Organizer

- **WHEN** the caller's Organizer is deactivated
- **THEN** it fails with FailedPrecondition

### Requirement: Get reads the caller's own account

Get SHALL take no input, call PayoutAccountUseCase.Get for the caller's own Organizer, and return the account's provider account ID and payout onboarding status. It SHALL return no onboarding link. When PayoutAccountUseCase.Get fails with NotFound because the Organizer has no payout account, Get SHALL fail with NotFound; a caller whose Organizer cannot be resolved has already failed the audience gate with PermissionDenied, so NotFound means only that no payout account exists yet.

#### Scenario: Member opens payout settings

- **WHEN** a member of an active Organizer with a pending account calls Get
- **THEN** it returns their Organizer's account and status, and no onboarding link

#### Scenario: No payout account yet

- **WHEN** a member of an active Organizer that has no payout account calls Get
- **THEN** it fails with NotFound

### Requirement: StartOnboarding returns a link for the caller's own account

StartOnboarding SHALL take no input, call PayoutAccountUseCase.StartOnboarding for the caller's own Organizer, and return the onboarding link it gives. When the Organizer is no longer found, it SHALL fail with PermissionDenied; any other failure, such as Unavailable, SHALL be returned unchanged.

#### Scenario: Member starts onboarding

- **WHEN** a member of an active Organizer calls StartOnboarding
- **THEN** it returns an onboarding link for their Organizer's account

#### Scenario: Organizer gone meanwhile

- **WHEN** PayoutAccountUseCase.StartOnboarding fails with NotFound
- **THEN** StartOnboarding fails with PermissionDenied
