# Spec Delta

## MODIFIED Requirements

### Requirement: The Admission of a ticket

GetByTicket SHALL return the Admission of the given Ticket together with the number of its Scanner, and SHALL fail with NotFound when the Ticket has no Admission.

#### Scenario: Admitted ticket

- **WHEN** the Ticket was admitted at 18:32 through Scanner 1
- **THEN** the Admission with 18:32 and Scanner number 1 is returned

#### Scenario: Ticket not admitted

- **WHEN** the Ticket has only been rejected
- **THEN** GetByTicket fails with NotFound
