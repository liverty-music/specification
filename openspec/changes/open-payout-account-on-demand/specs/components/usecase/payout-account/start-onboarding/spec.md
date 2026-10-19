## Purpose

PayoutAccountUseCase.StartOnboarding is called when a member of an Organizer asks to start or continue the payment provider's 本人確認 (identity check): it opens the Organizer's payout account when there is none and returns a fresh link to the provider's onboarding page.

## ADDED Requirements

### Requirement: StartOnboarding opens the account when the Organizer has none

StartOnboarding SHALL load the Organizer through Organizer.Get, failing with NotFound when it does not exist. When PayoutAccount.GetByOrganizerID finds no account, it SHALL open one through PayoutAccount.Create with the Organizer's owner email as contact and store it as pending through PayoutAccount.Upsert. When the Organizer already has an account, it SHALL open no other. When the account cannot be opened or stored, StartOnboarding SHALL fail with that error, such as Unavailable when the payment provider cannot be reached, and return no link.

#### Scenario: First start

- **WHEN** a member of an Organizer without an account calls StartOnboarding
- **THEN** an account is opened with the owner email as contact and stored as pending, and an onboarding link for it is returned

#### Scenario: Account already open

- **WHEN** the Organizer's stored account is pending or restricted
- **THEN** no account is opened and an onboarding link for the stored account is returned

#### Scenario: Provider unreachable when opening

- **WHEN** the account cannot be opened because the payment provider cannot be reached
- **THEN** StartOnboarding fails with Unavailable, no account is stored and no link is returned

#### Scenario: Unknown Organizer

- **WHEN** no Organizer has the id
- **THEN** StartOnboarding fails with NotFound and no account is opened

### Requirement: StartOnboarding returns a fresh onboarding link

StartOnboarding SHALL return a new link from PayoutAccount.CreateOnboardingLink on every call, whatever the account's status, with the organizer console's payout account settings as the address the provider brings the member back to. When the link cannot be created, StartOnboarding SHALL fail with that error, such as Unavailable, keeping any account it opened stored, so a later call returns a link for the same account.

#### Scenario: Two calls

- **WHEN** StartOnboarding is called twice for the same Organizer
- **THEN** each call returns a different link for the same account

#### Scenario: Link cannot be created

- **WHEN** the account was just opened and stored but the onboarding link cannot be created because the payment provider cannot be reached
- **THEN** StartOnboarding fails with Unavailable and the account stays stored as pending
