# Payment Events

## Purpose

Receives notices from the payment provider about the platform's charges and payouts, applies each at most once, and turns a dispute opened by a buyer's card issuer into a refund of the disputed Order.

## Requirements

### Requirement: Only authentic notices are accepted

The endpoint SHALL accept only notices signed with the platform's signing secret for this endpoint and at most 300 seconds old; any other notice SHALL be rejected with Unauthenticated and not applied. While no signing secret is configured, every notice SHALL be rejected with Unavailable.

#### Scenario: Forged notice

- **WHEN** a notice arrives with an invalid signature
- **THEN** it is rejected with Unauthenticated and nothing changes

#### Scenario: Endpoint not configured

- **WHEN** a notice arrives while no signing secret is configured
- **THEN** it is rejected with Unavailable

### Requirement: Each notice is applied at most once

Each notice SHALL be applied at most once however often it is delivered. A notice already applied SHALL be acknowledged without effect. A notice SHALL count as applied only after its handling succeeded; when handling fails, the endpoint SHALL answer with Internal so the provider delivers it again.

#### Scenario: Duplicate delivery

- **WHEN** the same notice is delivered twice
- **THEN** it is applied once and the second delivery is acknowledged without effect

#### Scenario: Handling fails

- **WHEN** handling a notice fails
- **THEN** the endpoint answers with Internal, the notice is not counted as applied, and a redelivery handles it again

### Requirement: A dispute refunds the Order

On a notice that a buyer opened a dispute, the endpoint SHALL find the Order with Order.GetByPaymentIntentRef using the notice's payment reference and call RefundOrderUseCase.RefundOrder for it with the reason Dispute and the time the notice was received. A dispute notice without a payment reference, or whose payment belongs to no Order, SHALL be acknowledged and left for manual review. When RefundOrder fails with anything other than NotFound, the endpoint SHALL answer with Internal.

#### Scenario: Dispute on a platform order

- **WHEN** a dispute notice names the payment of a Paid Order
- **THEN** RefundOrderUseCase.RefundOrder runs for that Order with the reason Dispute

#### Scenario: Dispute on an unknown payment

- **WHEN** a dispute notice names a payment that belongs to no Order
- **THEN** the notice is acknowledged and nothing changes

#### Scenario: Refund already applied

- **WHEN** a dispute notice arrives for an Order an admin already refunded
- **THEN** the Order stays Refunded and the notice is acknowledged

### Requirement: Other notices are acknowledged

Notices that a refund was applied, that a payout was reversed, or that the platform's own bank payout succeeded or failed, and notices of any other kind, SHALL be acknowledged without effect.

#### Scenario: Refund confirmation

- **WHEN** a notice confirms a refund the platform issued
- **THEN** it is acknowledged and nothing changes
