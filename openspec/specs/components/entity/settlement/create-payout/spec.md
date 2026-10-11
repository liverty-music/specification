# Settlement.CreatePayout

## Purpose

Pays one split of a Settlement from the platform to the payee Organizer's payout account, tied to the Order's captured charge, and returns the provider payout ID.

## Requirements

### Requirement: Pay out a split once

CreatePayout SHALL move the given amount, in the Order's currency, to the payee's payout account, tied to the given captured charge so it never exceeds that charge's funds, and return the provider payout ID; a repeated CreatePayout for the same Settlement and payee SHALL pay only once and return the same ID. It SHALL fail with InvalidArgument when the amount is zero or negative, and with Unavailable when payouts cannot be reached.

#### Scenario: Split paid out

- **WHEN** CreatePayout is called for a 14400 yen split against a captured charge
- **THEN** 14400 yen reaches the payee's payout account, tied to that charge, and a provider payout ID is returned

#### Scenario: Repeated payout

- **WHEN** CreatePayout is called again for the same Settlement and payee
- **THEN** nothing more is paid and the same ID is returned

#### Scenario: Non-positive amount

- **WHEN** CreatePayout is called with an amount of zero or less
- **THEN** it fails with InvalidArgument and nothing is paid
