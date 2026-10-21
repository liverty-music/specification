# Order.CreateRefund

## Purpose

Refunds an amount of an Order's captured charge to the fan's original payment method and returns the provider refund ID.

## Requirements

### Requirement: Refund once per order

CreateRefund SHALL take an Order, a charge, an amount and a purpose — the Order's own refund, or the refund of one named ResaleListing of the Order — refund the given amount of the given charge to the fan and return the provider refund ID. A repeated CreateRefund for the same Order and purpose SHALL refund only once and return the same ID; refunds for different purposes of the same Order are separate refunds, each of part of the charge. It SHALL fail with InvalidArgument when the amount is zero or negative, with FailedPrecondition when the charge is already fully refunded or the amount exceeds what is left of it, and with Unavailable when card payments cannot be reached.

#### Scenario: Refund issued

- **WHEN** CreateRefund is called for a 16000 yen charge with the amount 16000 for the Order's own refund
- **THEN** 16000 yen is returned to the fan's card and a provider refund ID is returned

#### Scenario: Repeated refund

- **WHEN** CreateRefund is called again for the same Order and purpose
- **THEN** no second refund is issued and the same ID is returned

#### Scenario: Two listings of one order

- **WHEN** CreateRefund is called for a 10000 yen charge with 4500 yen for one listing and then with 4500 yen for another listing of the same Order
- **THEN** two refunds of 4500 yen are issued with two different IDs

#### Scenario: More than is left

- **WHEN** 4500 yen of a 5000 yen charge was refunded and CreateRefund is called with 1000 yen for the Order's own refund
- **THEN** it fails with FailedPrecondition and nothing is refunded

#### Scenario: Non-positive amount

- **WHEN** the amount is zero or less
- **THEN** CreateRefund fails with InvalidArgument and nothing is refunded
