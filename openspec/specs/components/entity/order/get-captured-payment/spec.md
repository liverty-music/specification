# Order.GetCapturedPayment

## Purpose

Reads a captured payment's amount, currency, payment service and card display facets, without charging anything.

## Requirements

### Requirement: Read a captured payment

GetCapturedPayment SHALL return the amount actually captured, its currency, the payment service holding it, and the card brand and last four digits when known; it SHALL never return the card number, security code or expiry, and SHALL never charge. It SHALL fail with FailedPrecondition when the payment has not been captured, with NotFound when no payment has the reference, and with Unavailable when card payments cannot be reached.

#### Scenario: Captured payment

- **WHEN** a captured payment of 16000 yen on a Visa card ending 4242 is read
- **THEN** 16000, JPY, the payment service, Visa and 4242 are returned

#### Scenario: Not captured

- **WHEN** the payment is still a hold or was released
- **THEN** GetCapturedPayment fails with FailedPrecondition

#### Scenario: Unknown reference

- **WHEN** no payment has the reference
- **THEN** GetCapturedPayment fails with NotFound
