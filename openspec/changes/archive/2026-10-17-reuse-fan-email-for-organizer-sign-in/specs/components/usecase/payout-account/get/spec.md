# Spec Delta

## MODIFIED Requirements

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
