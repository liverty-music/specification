# TicketUseCase.GetMyTickets

## Purpose

TicketUseCase.GetMyTickets returns every Ticket currently bound to the calling fan's account.

## Requirements

### Requirement: Caller's tickets

GetMyTickets SHALL return the Tickets whose holder is the calling fan, as listed by Ticket.ListByHolder, including Voided ones, and an empty list when the fan holds none.

#### Scenario: Fan with tickets

- **WHEN** a fan holding 2 Issued Tickets asks for their tickets
- **THEN** both Tickets are returned

#### Scenario: Fan without tickets

- **WHEN** a fan holding no Ticket asks for their tickets
- **THEN** an empty list is returned
