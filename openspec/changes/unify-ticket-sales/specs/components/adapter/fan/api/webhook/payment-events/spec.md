# Spec Delta

## MODIFIED Requirements

### Requirement: A dispute refunds the Order

On a notice that the card issuer of an Order's user opened a dispute, the endpoint SHALL find the Order with Order.GetByProviderPaymentID using the notice's provider payment ID and call OrderUseCase.Refund for it with the reason Dispute and the time the notice was received. A dispute notice without a provider payment ID, or whose payment belongs to no Order, SHALL be acknowledged and left for manual review. When OrderUseCase.Refund fails with anything other than NotFound, the endpoint SHALL answer with Internal.

#### Scenario: Dispute on a platform order

- **WHEN** a dispute notice names the payment of a Paid Order
- **THEN** OrderUseCase.Refund runs for that Order with the reason Dispute

#### Scenario: Dispute on an unknown payment

- **WHEN** a dispute notice names a payment that belongs to no Order
- **THEN** the notice is acknowledged and nothing changes

#### Scenario: Refund already applied

- **WHEN** a dispute notice arrives for an Order an admin already refunded
- **THEN** the Order stays Refunded and the notice is acknowledged
