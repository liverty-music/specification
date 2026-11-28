# Spec Delta

## Purpose

DisputeUseCase.SubmitEvidence answers a contested Dispute at the time Respond chose: it checks the answer against the current state and submits the evidence, gives an admin until 48 hours before the deadline when the answer is a review, or accepts the Dispute when the answer changed or the dispute cannot be contested.

```mermaid
sequenceDiagram
autonumber
participant UC as DisputeUseCase.SubmitEvidence
participant Dispute
participant Order
participant Event
participant Admission
participant Ticket
participant ResaleListing
participant User
participant Venue
UC->>Dispute: Sync
break no longer Open
  Note over UC: nothing more
end
UC->>Order: Get
UC->>Order: GetEventID
UC->>Event: Get
UC->>Order: GetProviderOwnRefund
UC->>Admission: CountByEvent
opt reason Fraud
  UC->>Order: IsCardholderAuthenticated
end
alt answer is now accept
  UC->>UC: as Respond's accept
else review, earlier than 48 hours before the due time
  Note over UC: page an admin, schedule again
else contest
  UC->>Ticket: ListByOrder
  loop each admitted Ticket
    UC->>Admission: GetByTicket
  end
  UC->>ResaleListing: ListByOrder
  UC->>User: Get
  UC->>Venue: Get
  UC->>Dispute: SubmitEvidence
  opt FailedPrecondition
    UC->>Dispute: Sync
    Note over UC: closed or escalated: stop; still Open: cannot be contested, accept
  end
end
```

## ADDED Requirements

### Requirement: The answer is checked again

SubmitEvidence SHALL sync the Dispute with Dispute.Sync and do nothing when it is no longer Open. It SHALL then decide again as Respond does, from the Order, its Event, Order.GetProviderOwnRefund, Admission.CountByEvent and, for the reason Fraud, Order.IsCardholderAuthenticated, read at this time. When the answer is now to accept, it SHALL accept as Respond does. When the answer is to review and it is earlier than 48 hours before the evidence due time, it SHALL page an admin and schedule itself again for that time, so the admin has until then to answer; at that time a review is contested.

#### Scenario: Event cancelled after the dispute opened
- **WHEN** SubmitEvidence runs for an Open NotReceived Dispute whose Paid Order's Event became CANCELLED after the dispute opened
- **THEN** the Dispute is Accepted and DisputeUseCase.Settle runs for it

#### Scenario: Already closed
- **WHEN** SubmitEvidence runs for a Dispute the payment provider reports won
- **THEN** the Dispute is Won and nothing is submitted

#### Scenario: Nobody entered the concert
- **WHEN** SubmitEvidence runs 24 hours after the Event's start for an Open NotReceived Dispute due in 10 days, and no Ticket of the Event was admitted
- **THEN** an admin is paged and SubmitEvidence is scheduled again for 48 hours before the evidence due time

#### Scenario: Admin already answered
- **WHEN** SubmitEvidence runs for a Duplicate Dispute an admin already accepted with the payment provider
- **THEN** nothing is submitted

### Requirement: Evidence gathered and submitted

To contest, SubmitEvidence SHALL gather the Order's Tickets with Ticket.ListByOrder, the Admission of each admitted Ticket with Admission.GetByTicket, the resale refunds from the Order's payment with ResaleListing.ListByOrder, the account with User.Get and the Event's Venue with Venue.Get, and submit them with the purchase, the refund terms and the Order's own refund through Dispute.SubmitEvidence. When the account no longer exists (User.Get fails with NotFound, as after the fan deleted it), the evidence is submitted without it. When Dispute.SubmitEvidence fails with FailedPrecondition, SubmitEvidence SHALL sync the Dispute: when it is closed or escalated, it SHALL stop (an escalation is answered by its own Respond); when it is still Open, the dispute cannot be contested and SubmitEvidence SHALL accept it as Respond does. A call that fails with Unavailable or ResourceExhausted SHALL be retried until 1 hour before the evidence due time, or for 1 hour when that is sooner; after that, or on any other failure, SubmitEvidence SHALL end with the error and the Dispute stays Open.

#### Scenario: Attended concert
- **WHEN** SubmitEvidence runs after the Event for an Open NotReceived Dispute whose two Tickets were admitted
- **THEN** the evidence with both Admissions is submitted and the Dispute is Contested

#### Scenario: One ticket resold
- **WHEN** SubmitEvidence runs for an Order one of whose two Tickets was resold and its user refunded
- **THEN** the evidence includes that resale refund with its amount and time

#### Scenario: Account deleted
- **WHEN** SubmitEvidence runs for an Order whose fan deleted their account after the concert
- **THEN** the evidence is submitted without the account

#### Scenario: Dispute that cannot be contested
- **WHEN** Dispute.SubmitEvidence fails with FailedPrecondition and the synced Dispute is still Open
- **THEN** the Dispute is Accepted and DisputeUseCase.Settle runs for it

#### Scenario: Payment provider down until the deadline
- **WHEN** Dispute.SubmitEvidence fails with Unavailable until 1 hour before the evidence due time
- **THEN** SubmitEvidence ends with Unavailable and the Dispute stays Open
