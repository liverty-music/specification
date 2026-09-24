# Settlement.ReverseTransfer

## Purpose

Claws back one paid-out split from the payee's payout account to the platform and returns the reversal's reference.

## Requirements

### Requirement: Reverse a payout once

ReverseTransfer SHALL move the given amount of the given payout back to the platform and return the reversal reference; a repeated ReverseTransfer for the same Settlement and payout SHALL reverse only once and return the same reference. It SHALL fail with InvalidArgument when the amount is zero or negative, and with Unavailable when payouts cannot be reached.

#### Scenario: Payout reversed

- **WHEN** ReverseTransfer is called for a 14400 yen payout with the amount 14400
- **THEN** 14400 yen returns to the platform and a reversal reference is returned

#### Scenario: Repeated reversal

- **WHEN** ReverseTransfer is called again for the same Settlement and payout
- **THEN** nothing more is reversed and the same reference is returned

#### Scenario: Non-positive amount

- **WHEN** the amount is zero or less
- **THEN** ReverseTransfer fails with InvalidArgument
