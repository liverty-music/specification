# Spec Delta

## MODIFIED Requirements

### Requirement: Caller's tickets

GetMyTickets SHALL return the Tickets whose user is the calling fan, as listed by Ticket.ListByUser, including Voided ones, and an empty list when the fan has none.

#### Scenario: Fan with tickets
- **WHEN** a fan with 2 Issued Tickets asks for their tickets
- **THEN** both Tickets are returned

#### Scenario: Fan without tickets
- **WHEN** a fan with no Ticket asks for their tickets
- **THEN** an empty list is returned
