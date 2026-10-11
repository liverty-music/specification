# PayoutAccount.GetStatus

## Purpose

Reads an account's current payout onboarding status from the payment provider.

## Requirements

### Requirement: GetStatus reports the provider's current readiness

GetStatus SHALL return active when the provider allows the account to receive payouts, pending when that permission is still being reviewed or has not been requested yet, and restricted when the provider has turned it off. It SHALL fail with NotFound when the provider has no such account, and with Unavailable when the provider cannot be reached.

#### Scenario: Identity check cleared

- **WHEN** the provider allows the account to receive payouts
- **THEN** GetStatus returns active

#### Scenario: Identity check in progress

- **WHEN** the provider is still reviewing the account
- **THEN** GetStatus returns pending

#### Scenario: Payouts turned off

- **WHEN** the provider has turned off payouts to the account
- **THEN** GetStatus returns restricted

#### Scenario: Provider unreachable

- **WHEN** the provider cannot be reached
- **THEN** GetStatus fails with Unavailable
