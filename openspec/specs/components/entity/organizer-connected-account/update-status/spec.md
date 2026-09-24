# OrganizerConnectedAccount.UpdateStatus

## Purpose

Changes the stored payout onboarding status of an Organizer's connected account.

## Requirements

### Requirement: UpdateStatus changes only the status

UpdateStatus SHALL set the stored account's status to the given status and leave its account reference unchanged, and SHALL fail with NotFound when the Organizer has no stored account.

#### Scenario: Stored account

- **WHEN** a pending account is updated to active
- **THEN** its status becomes active and its account reference is unchanged

#### Scenario: No account

- **WHEN** the Organizer has no stored account
- **THEN** UpdateStatus fails with NotFound
