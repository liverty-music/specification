# Spec Delta

## ADDED Requirements

### Requirement: Refused while the payment is disputed

Create SHALL fail with FailedPrecondition, listing nothing, while the Ticket's Order is disputed (an open or unsettled Dispute) when the listing would be stored: the check and the insert are one atomic step, so a Dispute recorded at the same moment is either seen or recorded after the listing, in which case the Dispute's response cancels it.

#### Scenario: Ticket of a disputed order
- **WHEN** Create is called for an Issued Ticket whose Order has an Open Dispute
- **THEN** it fails with FailedPrecondition and nothing is listed

#### Scenario: Dispute won
- **WHEN** Create is called for an Issued Ticket whose Order's only Dispute is Won
- **THEN** the listing is stored
