# components/entity/order/get-by-checkout-id Specification

## Purpose
Reads the Order a Checkout names, by the Checkout's id, in any status.

## Requirements

### Requirement: The checkout's order

GetByCheckoutID SHALL return the Order the given Checkout names, in any status, and SHALL fail with NotFound when no Checkout has the id.

#### Scenario: Paid checkout
- **WHEN** a Completed Checkout's Order is read
- **THEN** that Order is returned, Paid

#### Scenario: Checkout not paid
- **WHEN** a Held Checkout's Order is read
- **THEN** that Order is returned, Pending

#### Scenario: Unknown checkout
- **WHEN** no Checkout has the id
- **THEN** GetByCheckoutID fails with NotFound
