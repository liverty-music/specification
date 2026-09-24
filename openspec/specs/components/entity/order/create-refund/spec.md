# Order.CreateRefund

## Purpose

Refunds an amount of an Order's captured charge to the buyer's original payment method and returns the refund's reference.

## Requirements

### Requirement: Refund once per order

CreateRefund SHALL refund the given amount of the given charge to the buyer and return the refund reference; a repeated CreateRefund for the same Order SHALL refund only once and return the same reference. It SHALL fail with InvalidArgument when the amount is zero or negative, with FailedPrecondition when the charge is already fully refunded, and with Unavailable when card payments cannot be reached.

#### Scenario: Refund issued

- **WHEN** CreateRefund is called for a 16000 yen charge with the amount 16000
- **THEN** 16000 yen is returned to the buyer's card and a refund reference is returned

#### Scenario: Repeated refund

- **WHEN** CreateRefund is called again for the same Order
- **THEN** no second refund is issued and the same reference is returned

#### Scenario: Non-positive amount

- **WHEN** the amount is zero or less
- **THEN** CreateRefund fails with InvalidArgument and nothing is refunded
