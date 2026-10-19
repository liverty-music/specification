# PayoutAccountUseCase.Get

## Purpose

PayoutAccountUseCase.Get returns an Organizer's payout-receiving account and its payout onboarding status, refreshed from the payment provider. It only reads: PayoutAccountUseCase.StartOnboarding opens the account and gives the link to the 本人確認 (identity check).

## Requirements

### Requirement: The first call opens the account

Get SHALL load the Organizer through Organizer.Get, failing with NotFound when it does not exist. When PayoutAccount.GetByOrganizerID finds no account, it SHALL open one through PayoutAccount.Create with the Organizer's owner email as contact, store it as pending through PayoutAccount.Upsert, and return it with a link from PayoutAccount.CreateOnboardingLink that brings the organizer back to the organizer console's payout settings. When the account cannot be opened or stored, it SHALL fail with that error, such as Unavailable when the payment provider cannot be reached.

#### Scenario: First call

- **WHEN** an Organizer without an account calls Get
- **THEN** an account is opened with the owner email as contact and stored as pending, and it is returned with an onboarding link

#### Scenario: Provider unreachable on first call

- **WHEN** the account cannot be opened because the payment provider cannot be reached
- **THEN** Get fails with Unavailable and no account is stored

#### Scenario: Unknown Organizer

- **WHEN** no Organizer has the id
- **THEN** Get fails with NotFound

### Requirement: Later calls refresh the status

When the Organizer already has an account, Get SHALL read its current status through PayoutAccount.GetStatus and, when it differs from the stored one, store it through PayoutAccount.UpdateStatus and return the new status. When the status cannot be read, it SHALL return the stored status; when the new status cannot be stored, it SHALL still return the new status.

#### Scenario: Identity check just cleared

- **WHEN** the stored status is pending and the provider now reports active
- **THEN** the stored status becomes active and active is returned

#### Scenario: Status cannot be read

- **WHEN** the current status cannot be read from the provider
- **THEN** the stored status is returned and the call succeeds

### Requirement: A link is given only while action is needed

Get SHALL return no onboarding link when the account is payout-eligible, and a fresh link on every call while it is pending or restricted. When a link cannot be created, it SHALL return the account without a link instead of failing.

#### Scenario: Active account

- **WHEN** the account's status is active
- **THEN** the account is returned without an onboarding link

#### Scenario: Pending or restricted account

- **WHEN** the account's status is pending or restricted
- **THEN** the account is returned with a new onboarding link

#### Scenario: Link cannot be created

- **WHEN** the onboarding link cannot be created
- **THEN** the account is returned without a link and the call succeeds
