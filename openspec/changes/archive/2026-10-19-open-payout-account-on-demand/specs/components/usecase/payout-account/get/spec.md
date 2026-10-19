## ADDED Requirements

### Requirement: Get only reads the stored account

Get SHALL return the Organizer's account found through PayoutAccount.GetByOrganizerID, and SHALL fail with NotFound when the Organizer has no stored account. Get SHALL never open an account at the payment provider and never create an onboarding link; opening the account and creating a link belong to PayoutAccountUseCase.StartOnboarding.

#### Scenario: Organizer without an account

- **WHEN** an Organizer that has no stored account calls Get
- **THEN** Get fails with NotFound, and no account is opened at the payment provider and none is stored

#### Scenario: Organizer with an account

- **WHEN** an Organizer whose stored account is pending calls Get
- **THEN** Get returns that account with its provider account ID and status, and no onboarding link is created

## REMOVED Requirements

### Requirement: The first call opens the account

**Reason**: Reading the payout account must not open one at the payment provider; an Organizer's account is opened only when a member asks to start onboarding.
**Migration**: PayoutAccountUseCase.StartOnboarding opens the account when the Organizer has none. Get now fails with NotFound in that case ("Get only reads the stored account").

### Requirement: A link is given only while action is needed

**Reason**: Get no longer creates onboarding links; a link is single-use and is created only when the member is about to use it.
**Migration**: PayoutAccountUseCase.StartOnboarding returns a fresh onboarding link on every call.
