# OrganizerConnectedAccount.CreateConnectedAccount

## Purpose

Opens an Organizer's payout-receiving account at the payment provider and returns its account reference.

## Requirements

### Requirement: CreateConnectedAccount opens a receive-only account

CreateConnectedAccount SHALL open an account at the payment provider for the Organizer, in Japan and in JPY, that can receive transfers from the platform and cannot accept card payments, with the platform bearing any negative balance on it and collecting its fees. The account SHALL carry the given contact email and no other personal data: the Organizer gives their identity details directly to the provider during the identity check, so the account starts unverified. It SHALL return the account reference.

#### Scenario: Account is opened

- **WHEN** CreateConnectedAccount runs for an Organizer with a contact email
- **THEN** it returns the reference of a new unverified account that can receive transfers only

### Requirement: CreateConnectedAccount does not open a second account on retry

A repeated call for the same Organizer within 24 hours SHALL return the account the first call opened instead of opening another.

#### Scenario: Retried call

- **WHEN** CreateConnectedAccount runs twice for the same Organizer within 24 hours
- **THEN** both calls return the same account reference

### Requirement: CreateConnectedAccount failures

CreateConnectedAccount SHALL fail with InvalidArgument when the Organizer or the contact email is missing, and with Unavailable when the payment provider cannot be reached or payouts are not set up on the platform.

#### Scenario: Missing contact email

- **WHEN** the contact email is empty
- **THEN** it fails with InvalidArgument and no account is opened

#### Scenario: Provider unreachable

- **WHEN** the payment provider cannot be reached
- **THEN** it fails with Unavailable
