# Spec Delta

## ADDED Requirements

### Requirement: A completed charge is fulfilled

On a notice that a charge completed, the endpoint SHALL call IssuanceUseCase.FulfillPayment with the notice's payment reference. When FulfillPayment fails, the endpoint SHALL answer with Internal, so the provider delivers the notice again.

#### Scenario: Checkout charge completes

- **WHEN** a notice reports that the charge of a fan's checkout completed
- **THEN** IssuanceUseCase.FulfillPayment runs for its payment reference

#### Scenario: Fulfillment fails

- **WHEN** FulfillPayment fails
- **THEN** the endpoint answers with Internal, the notice is not counted as applied, and a redelivery fulfills it

## MODIFIED Requirements

### Requirement: Other notices are acknowledged

Notices that a refund was applied, that a payout was reversed, or that the platform's own bank payout succeeded or failed, and notices of any other kind than a dispute or a completed charge, SHALL be acknowledged without effect.

#### Scenario: Refund confirmation

- **WHEN** a notice confirms a refund the platform issued
- **THEN** it is acknowledged and nothing changes
