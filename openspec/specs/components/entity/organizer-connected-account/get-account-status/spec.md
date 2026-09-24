# OrganizerConnectedAccount.GetAccountStatus

## Purpose

Reads an account's current payout onboarding status from the payment provider.

## Requirements

### Requirement: GetAccountStatus reports the provider's current readiness

GetAccountStatus SHALL return active when the provider allows the account to receive transfers, pending when that permission is still being reviewed or has not been requested yet, and restricted when the provider has turned it off. It SHALL fail with NotFound when the provider has no such account, and with Unavailable when the provider cannot be reached.

#### Scenario: Identity check cleared

- **WHEN** the provider allows the account to receive transfers
- **THEN** GetAccountStatus returns active

#### Scenario: Identity check in progress

- **WHEN** the provider is still reviewing the account
- **THEN** GetAccountStatus returns pending

#### Scenario: Transfers turned off

- **WHEN** the provider has turned off transfers to the account
- **THEN** GetAccountStatus returns restricted

#### Scenario: Provider unreachable

- **WHEN** the provider cannot be reached
- **THEN** GetAccountStatus fails with Unavailable
