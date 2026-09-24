# Ticket.ListByHolder

## Purpose

Lists the Tickets currently bound to one account.

## Requirements

### Requirement: Tickets of a holder

ListByHolder SHALL return every Ticket whose holder is the given account, Issued and Voided alike, most recently issued first, and SHALL return an empty list when the account holds none.

#### Scenario: Holder with tickets

- **WHEN** the account holds a Ticket issued on 1 May and one issued on 3 May
- **THEN** both are returned, the 3 May Ticket first

#### Scenario: Voided tickets included

- **WHEN** one of the account's Tickets is Voided
- **THEN** it is returned with status Voided

#### Scenario: No tickets

- **WHEN** the account holds no Ticket
- **THEN** an empty list is returned
