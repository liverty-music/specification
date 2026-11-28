# Spec Delta

## RENAMED Requirements

- FROM: `### Requirement: A dispute refunds the Order`
- TO: `### Requirement: A dispute is answered`

## MODIFIED Requirements

### Requirement: A dispute is answered

On a notice that the card issuer of an Order's user opened a dispute, the endpoint SHALL find the Order with Order.GetByProviderPaymentID using the notice's provider payment ID and start DisputeUseCase.Respond for that Order and the provider dispute ID, at most once per provider dispute. On a notice that the payment provider took the disputed money back, the endpoint SHALL start DisputeUseCase.Respond for that Order and dispute as an escalation, at most once per provider dispute, whether or not the dispute was recorded yet: Respond reads the dispute's current state from the payment provider. A dispute notice without a provider payment ID, or whose payment belongs to no Order, SHALL be acknowledged and left for manual review. When the lookup fails with anything other than NotFound, or Respond cannot be started, the endpoint SHALL answer with Internal.

#### Scenario: Dispute on a platform order

- **WHEN** a dispute notice names the payment of a Paid Order
- **THEN** DisputeUseCase.Respond starts for that Order and that dispute

#### Scenario: Dispute on an unknown payment

- **WHEN** a dispute notice names a payment that belongs to no Order
- **THEN** the notice is acknowledged and nothing changes

#### Scenario: Refund already applied

- **WHEN** a dispute notice arrives for an Order an admin already refunded for a 中止
- **THEN** DisputeUseCase.Respond starts for it, which contests the dispute with the refund as evidence

#### Scenario: Notice delivered again after its handling failed

- **WHEN** a dispute notice is delivered again for a provider dispute whose Respond already started
- **THEN** no second Respond starts and the notice is acknowledged

#### Scenario: Inquiry escalated

- **WHEN** a notice reports that the payment provider took back the money of a dispute that started as an inquiry
- **THEN** DisputeUseCase.Respond starts for the escalation, even when the notice that opened the dispute has not been handled yet

## ADDED Requirements

### Requirement: A closed dispute is settled

On a notice that a dispute against an Order's payment closed, the endpoint SHALL find the Order with Order.GetByProviderPaymentID and start DisputeUseCase.Settle for it with the provider dispute ID and the outcome: Won when the dispute was won, or when an inquiry closed without becoming a chargeback, and Lost when it was lost or resolved by a prevention service that refunded the cardholder. It SHALL start Settle at most once per provider dispute and outcome, sharing the Lost one with the Settle that an accepted dispute starts. A notice for a payment that belongs to no Order SHALL be acknowledged and left for manual review. When the lookup fails with anything other than NotFound, or Settle cannot be started, the endpoint SHALL answer with Internal.

#### Scenario: Dispute won

- **WHEN** a notice reports that a dispute against a Paid Order's payment was won
- **THEN** DisputeUseCase.Settle starts for it with the outcome Won

#### Scenario: Accepted dispute closed

- **WHEN** a notice reports lost for a dispute the platform accepted, whose Settle already started
- **THEN** no second Settle starts and the notice is acknowledged

#### Scenario: Lost dispute later won

- **WHEN** a notice reports won for a dispute whose Settle with the outcome Lost already ran
- **THEN** DisputeUseCase.Settle starts with the outcome Won

#### Scenario: Inquiry closed

- **WHEN** a notice reports that an inquiry against an Order's payment closed without a chargeback
- **THEN** DisputeUseCase.Settle starts for it with the outcome Won
