# Spec Delta

## MODIFIED Requirements

### Requirement: Reverse a payout once

ReversePayout SHALL take a Settlement, a payout, an amount and the claw-back it is for (the Order's refund, or one Dispute), move that amount of the payout back to the platform and return the provider payout reversal ID. A repeated ReversePayout for the same Settlement, payout and claw-back SHALL reverse only once and return the same ID, however long after the first one it runs, including when the payout has since been fully reversed. Claw-backs for different Disputes of the same payout are separate reversals. It SHALL fail with InvalidArgument when the amount is zero or negative, with FailedPrecondition when less than the amount is left to reverse, and with Unavailable when payouts cannot be reached.

#### Scenario: Payout reversed

- **WHEN** ReversePayout is called for a 14400 yen payout with the amount 14400 for the Order's refund
- **THEN** 14400 yen returns to the platform and a provider payout reversal ID is returned

#### Scenario: Repeated reversal

- **WHEN** ReversePayout is called again for the same Settlement, payout and claw-back
- **THEN** nothing more is reversed and the same ID is returned

#### Scenario: Repeated days later

- **WHEN** ReversePayout is called again for the same Settlement, payout and claw-back 3 days after the payout was fully reversed
- **THEN** nothing more is reversed and the first reversal's ID is returned

#### Scenario: Two partial disputes

- **WHEN** ReversePayout is called for 4750 yen of a 9500 yen payout for one Dispute and then for 2375 yen for another
- **THEN** two reversals are made and 2375 yen of the payout is left

#### Scenario: Non-positive amount

- **WHEN** the amount is zero or less
- **THEN** ReversePayout fails with InvalidArgument
