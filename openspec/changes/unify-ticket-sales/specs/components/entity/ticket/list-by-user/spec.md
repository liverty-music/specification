# Spec Delta

## Purpose

Lists the Tickets bound to one User.

## ADDED Requirements

### Requirement: Tickets of a user

ListByUser SHALL return every Ticket whose user is the given User, Issued and Voided alike, most recently issued first, and SHALL return an empty list when the User has none.

#### Scenario: User with tickets
- **WHEN** the User has a Ticket issued on 1 May and one issued on 3 May
- **THEN** both are returned, the 3 May Ticket first

#### Scenario: Voided tickets included
- **WHEN** one of the User's Tickets is Voided
- **THEN** it is returned with status Voided

#### Scenario: No tickets
- **WHEN** the User has no Ticket
- **THEN** an empty list is returned
