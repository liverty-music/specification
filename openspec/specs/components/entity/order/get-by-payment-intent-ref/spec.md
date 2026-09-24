# Order.GetByPaymentIntentRef

## Purpose

Returns the Order whose captured payment has the given payment reference.

## Requirements

### Requirement: Order of a payment

GetByPaymentIntentRef SHALL return the Order whose payment reference equals the given reference and SHALL fail with NotFound when no Order has it.

#### Scenario: Known payment

- **WHEN** an Order's payment reference matches
- **THEN** that Order is returned

#### Scenario: Payment not made on the platform

- **WHEN** no Order has the payment reference
- **THEN** GetByPaymentIntentRef fails with NotFound
