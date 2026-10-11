# Order.GetByProviderPaymentID

## Purpose

Returns the Order whose captured payment has the given provider payment ID.

## Requirements

### Requirement: Order of a payment

GetByProviderPaymentID SHALL return the Order whose provider payment ID equals the given ID and SHALL fail with NotFound when no Order has it.

#### Scenario: Known payment

- **WHEN** an Order's provider payment ID matches
- **THEN** that Order is returned

#### Scenario: Payment not made on the platform

- **WHEN** no Order has the provider payment ID
- **THEN** GetByProviderPaymentID fails with NotFound
