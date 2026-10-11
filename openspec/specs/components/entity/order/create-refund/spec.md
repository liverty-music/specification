# Order.CreateRefund

## Purpose

Refunds an amount of an Order's captured charge to the buyer's original payment method and returns the provider refund ID.

## Requirements

### Requirement: Refund once per order

CreateRefund SHALL refund the given amount of the given charge to the buyer and return the provider refund ID; a repeated CreateRefund for the same Order SHALL refund only once and return the same ID. It SHALL fail with InvalidArgument when the amount is zero or negative, with FailedPrecondition when the charge is already fully refunded, and with Unavailable when card payments cannot be reached.

#### Scenario: Refund issued

- **WHEN** CreateRefund is called for a 16000 yen charge with the amount 16000
- **THEN** 16000 yen is returned to the buyer's card and a provider refund ID is returned

#### Scenario: Repeated refund

- **WHEN** CreateRefund is called again for the same Order
- **THEN** no second refund is issued and the same ID is returned

#### Scenario: Non-positive amount

- **WHEN** the amount is zero or less
- **THEN** CreateRefund fails with InvalidArgument and nothing is refunded
