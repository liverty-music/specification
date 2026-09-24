# Settlement.CreateTransfer

## Purpose

Pays one split of a Settlement from the platform to the payee Organizer's payout account, tied to the Order's captured charge, and returns the payout's reference.

## Requirements

### Requirement: Pay out a split once

CreateTransfer SHALL move the given amount, in the Order's currency, to the payee's payout account, tied to the given captured charge so it never exceeds that charge's funds, and return the payout reference; a repeated CreateTransfer for the same Settlement and payee SHALL pay only once and return the same reference. It SHALL fail with InvalidArgument when the amount is zero or negative, and with Unavailable when payouts cannot be reached.

#### Scenario: Split paid out

- **WHEN** CreateTransfer is called for a 14400 yen split against a captured charge
- **THEN** 14400 yen reaches the payee's payout account, tied to that charge, and a payout reference is returned

#### Scenario: Repeated payout

- **WHEN** CreateTransfer is called again for the same Settlement and payee
- **THEN** nothing more is paid and the same reference is returned

#### Scenario: Non-positive amount

- **WHEN** CreateTransfer is called with an amount of zero or less
- **THEN** it fails with InvalidArgument and nothing is paid
