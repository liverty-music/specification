# components/entity/order/get-by-checkout-id Specification

## Purpose
Reads the Order paid for a Checkout, if there is one.

## Requirements

### Requirement: The checkout's order

GetByCheckoutID SHALL return the Order whose source is the given Checkout, and SHALL fail with NotFound when there is none.

#### Scenario: Paid checkout
- **WHEN** a Completed Checkout's Order is read
- **THEN** that Order is returned

#### Scenario: Checkout not paid
- **WHEN** the Checkout has no Order
- **THEN** GetByCheckoutID fails with NotFound
