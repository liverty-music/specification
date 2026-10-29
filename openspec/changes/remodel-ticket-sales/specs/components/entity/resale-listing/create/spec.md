# Spec Delta

## MODIFIED Requirements

### Requirement: One open listing per ticket

Create SHALL store a Listed ResaleListing with the given Ticket, its Order, user, TicketStock, price and create time, and return it. Checking and storing SHALL be one indivisible step: it SHALL fail with AlreadyExists when the Ticket already has a Listed listing, and with FailedPrecondition when the Ticket is not Issued or has an admit time at that moment, storing nothing in both cases. A Ticket whose earlier listing was Withdrawn or Cancelled, or expired, SHALL be listable again. It SHALL fail with NotFound when no Ticket has the id.

#### Scenario: First listing
- **WHEN** Create is called for an Issued, not admitted Ticket without a listing
- **THEN** a Listed ResaleListing with the Ticket's TicketStock and its SeatType's price is stored and returned

#### Scenario: Listed twice
- **WHEN** two Create calls for the same Ticket run at the same time
- **THEN** one stores a listing and the other fails with AlreadyExists

#### Scenario: Ticket voided meanwhile
- **WHEN** the Ticket was Voided by a refund just before Create
- **THEN** Create fails with FailedPrecondition and stores nothing

#### Scenario: Listed again after withdrawing
- **WHEN** the Ticket's only earlier listing is Withdrawn
- **THEN** Create stores a new Listed listing
