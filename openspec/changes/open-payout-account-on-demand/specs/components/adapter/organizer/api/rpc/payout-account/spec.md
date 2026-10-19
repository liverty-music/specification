## ADDED Requirements

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

## REMOVED Requirements

### Requirement: Get returns the caller's own account

**Reason**: Get no longer returns an onboarding link, and its NotFound now means that the Organizer has no payout account, which the caller handles, instead of an Organizer gone meanwhile.
**Migration**: Replaced by "Get reads the caller's own account"; the onboarding link comes from StartOnboarding ("StartOnboarding returns a link for the caller's own account").
