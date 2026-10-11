# Order.GetProviderChargeID

## Purpose

Returns the provider charge ID of an Order's payment: the payment provider's ID for the captured charge, which refunds and payouts are tied to.

## Requirements

### Requirement: Resolve the captured charge

GetProviderChargeID SHALL return the provider charge ID of the payment's captured charge. It SHALL fail with FailedPrecondition when the payment has not been captured or has no charge, with NotFound when no payment has the provider payment ID, and with Unavailable when card payments cannot be reached.

#### Scenario: Captured payment

- **WHEN** the payment has been captured
- **THEN** its provider charge ID is returned

#### Scenario: Not captured

- **WHEN** the payment has not been captured
- **THEN** GetProviderChargeID fails with FailedPrecondition
