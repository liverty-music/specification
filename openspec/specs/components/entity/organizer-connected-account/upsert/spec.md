# OrganizerConnectedAccount.Upsert

## Purpose

Stores an Organizer's connected account, replacing the one already stored for that Organizer.

## Requirements

### Requirement: Upsert keeps one account per Organizer

Upsert SHALL store the account when the Organizer has none, and SHALL replace the account reference and status of the stored account when the Organizer already has one, so an Organizer never has two accounts.

#### Scenario: First account

- **WHEN** the Organizer has no stored account
- **THEN** the account is stored

#### Scenario: Account already stored

- **WHEN** the Organizer already has a stored account
- **THEN** its account reference and status are replaced and no second account is stored
