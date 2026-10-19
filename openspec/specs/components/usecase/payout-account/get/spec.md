# PayoutAccountUseCase.Get

## Purpose

PayoutAccountUseCase.Get returns an Organizer's payout-receiving account and its payout onboarding status, refreshed from the payment provider. It only reads: PayoutAccountUseCase.StartOnboarding opens the account and gives the link to the 本人確認 (identity check).

## Requirements

### Requirement: Later calls refresh the status

When the Organizer already has an account, Get SHALL read its current status through PayoutAccount.GetStatus and, when it differs from the stored one, store it through PayoutAccount.UpdateStatus and return the new status. When the status cannot be read, it SHALL return the stored status; when the new status cannot be stored, it SHALL still return the new status.

#### Scenario: Identity check just cleared

- **WHEN** the stored status is pending and the provider now reports active
- **THEN** the stored status becomes active and active is returned

#### Scenario: Status cannot be read

- **WHEN** the current status cannot be read from the provider
- **THEN** the stored status is returned and the call succeeds

### Requirement: Get only reads the stored account

Get SHALL return the Organizer's account found through PayoutAccount.GetByOrganizerID, and SHALL fail with NotFound when the Organizer has no stored account. Get SHALL never open an account at the payment provider and never create an onboarding link; opening the account and creating a link belong to PayoutAccountUseCase.StartOnboarding.

#### Scenario: Organizer without an account

- **WHEN** an Organizer that has no stored account calls Get
- **THEN** Get fails with NotFound, and no account is opened at the payment provider and none is stored

#### Scenario: Organizer with an account

- **WHEN** an Organizer whose stored account is pending calls Get
- **THEN** Get returns that account with its provider account ID and status, and no onboarding link is created
