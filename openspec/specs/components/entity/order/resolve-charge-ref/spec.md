# Order.ResolveChargeRef

## Purpose

Resolves an Order's payment reference to the reference of its captured charge, which refunds and payouts are tied to.

## Requirements

### Requirement: Resolve the captured charge

ResolveChargeRef SHALL return the reference of the payment's captured charge. It SHALL fail with FailedPrecondition when the payment has not been captured or has no charge, with NotFound when no payment has the reference, and with Unavailable when card payments cannot be reached.

#### Scenario: Captured payment

- **WHEN** the payment has been captured
- **THEN** its charge reference is returned

#### Scenario: Not captured

- **WHEN** the payment has not been captured
- **THEN** ResolveChargeRef fails with FailedPrecondition
