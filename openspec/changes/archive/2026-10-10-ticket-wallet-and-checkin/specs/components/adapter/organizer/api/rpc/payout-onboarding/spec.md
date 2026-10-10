# Spec Delta

## RENAMED Requirements

- FROM: `### Requirement: GetPayoutOnboarding returns the caller's own account`
- TO: `### Requirement: Get returns the caller's own account`

## MODIFIED Requirements

### Requirement: Get returns the caller's own account

Get SHALL take no input, call OnboardingUseCase.GetOrCreateOnboarding for the caller's own Organizer, and return the account's reference and payout onboarding status, with the onboarding link only when one was returned. When the Organizer is no longer found, it SHALL fail with PermissionDenied.

#### Scenario: Operator opens payout settings

- **WHEN** an operator of an active Organizer calls Get
- **THEN** it returns their Organizer's account and status, with an onboarding link while the account is not active

#### Scenario: Organizer gone meanwhile

- **WHEN** OnboardingUseCase.GetOrCreateOnboarding fails with NotFound
- **THEN** Get fails with PermissionDenied
