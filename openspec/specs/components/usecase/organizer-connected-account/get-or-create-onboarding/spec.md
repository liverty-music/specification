# OnboardingUseCase.GetOrCreateOnboarding

## Purpose

OnboardingUseCase.GetOrCreateOnboarding returns an Organizer's payout-receiving account and its payout onboarding status, opening the account on first use, and gives a link to continue the 本人確認 (identity check) while the account cannot yet receive payouts.

## Requirements

### Requirement: The first call opens the account

GetOrCreateOnboarding SHALL load the Organizer through Organizer.Get, failing with NotFound when it does not exist. When OrganizerConnectedAccount.GetByOrganizerID finds no account, it SHALL open one through OrganizerConnectedAccount.CreateConnectedAccount with the Organizer's operator email as contact, store it as pending through OrganizerConnectedAccount.Upsert, and return it with a link from OrganizerConnectedAccount.CreateOnboardingLink that brings the operator back to the organizer console's payout settings. When the account cannot be opened or stored, it SHALL fail with that error, such as Unavailable when the payment provider cannot be reached.

#### Scenario: First call

- **WHEN** an Organizer without an account calls GetOrCreateOnboarding
- **THEN** an account is opened and stored as pending, and it is returned with an onboarding link

#### Scenario: Provider unreachable on first call

- **WHEN** the account cannot be opened because the payment provider cannot be reached
- **THEN** GetOrCreateOnboarding fails with Unavailable and no account is stored

#### Scenario: Unknown Organizer

- **WHEN** no Organizer has the id
- **THEN** GetOrCreateOnboarding fails with NotFound

### Requirement: Later calls refresh the status

When the Organizer already has an account, GetOrCreateOnboarding SHALL read its current status through OrganizerConnectedAccount.GetAccountStatus and, when it differs from the stored one, store it through OrganizerConnectedAccount.UpdateStatus and return the new status. When the status cannot be read, it SHALL return the stored status; when the new status cannot be stored, it SHALL still return the new status.

#### Scenario: Identity check just cleared

- **WHEN** the stored status is pending and the provider now reports active
- **THEN** the stored status becomes active and active is returned

#### Scenario: Status cannot be read

- **WHEN** the current status cannot be read from the provider
- **THEN** the stored status is returned and the call succeeds

### Requirement: A link is given only while action is needed

GetOrCreateOnboarding SHALL return no onboarding link when the account is payout-eligible, and a fresh link on every call while it is pending or restricted. When a link cannot be created, it SHALL return the account without a link instead of failing.

#### Scenario: Active account

- **WHEN** the account's status is active
- **THEN** the account is returned without an onboarding link

#### Scenario: Pending or restricted account

- **WHEN** the account's status is pending or restricted
- **THEN** the account is returned with a new onboarding link

#### Scenario: Link cannot be created

- **WHEN** the onboarding link cannot be created
- **THEN** the account is returned without a link and the call succeeds
