# Spec Delta

## ADDED Requirements

### Requirement: No listing while the payment is disputed

Create SHALL return the FailedPrecondition that ResaleListing.Create returns while the Ticket's Order is disputed (an open or unsettled Dispute), listing nothing: a resale would refund the fan from the same payment the dispute is claiming back.

#### Scenario: Ticket of a disputed order
- **WHEN** a fan lists an Issued Ticket of a sold-out stock whose Order has an Open Dispute
- **THEN** Create fails with FailedPrecondition and nothing is listed

#### Scenario: Dispute won
- **WHEN** the fan lists the Ticket after the Order's only Dispute became Won
- **THEN** the Ticket is listed
