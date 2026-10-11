# Settlement.ReversePayout

## Purpose

Claws back one paid-out split from the payee's payout account to the platform and returns the provider payout reversal ID.

## Requirements

### Requirement: Reverse a payout once

ReversePayout SHALL move the given amount of the given payout back to the platform and return the provider payout reversal ID; a repeated ReversePayout for the same Settlement and payout SHALL reverse only once and return the same ID. It SHALL fail with InvalidArgument when the amount is zero or negative, and with Unavailable when payouts cannot be reached.

#### Scenario: Payout reversed

- **WHEN** ReversePayout is called for a 14400 yen payout with the amount 14400
- **THEN** 14400 yen returns to the platform and a provider payout reversal ID is returned

#### Scenario: Repeated reversal

- **WHEN** ReversePayout is called again for the same Settlement and payout
- **THEN** nothing more is reversed and the same ID is returned

#### Scenario: Non-positive amount

- **WHEN** the amount is zero or less
- **THEN** ReversePayout fails with InvalidArgument
