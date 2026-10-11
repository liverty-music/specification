# Spec Delta

## MODIFIED Requirements

### Requirement: Get returns the caller's own account

Get SHALL take no input, call PayoutAccountUseCase.Get for the caller's own Organizer, and return the account's provider account ID and payout onboarding status, with the onboarding link only when one was returned. When the Organizer is no longer found, it SHALL fail with PermissionDenied.

#### Scenario: Operator opens payout settings

- **WHEN** an operator of an active Organizer calls Get
- **THEN** it returns their Organizer's account and status, with an onboarding link while the account is not active

#### Scenario: Organizer gone meanwhile

- **WHEN** PayoutAccountUseCase.Get fails with NotFound
- **THEN** Get fails with PermissionDenied
