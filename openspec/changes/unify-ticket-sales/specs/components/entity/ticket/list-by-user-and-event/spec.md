# Spec Delta

## Purpose

Lists the Tickets one User has for one event.

## ADDED Requirements

### Requirement: Tickets of a user for an event

ListByUserAndEvent SHALL return every Ticket whose user is the given User and whose event is the given event, Issued and Voided alike, in the order they were issued, and SHALL return an empty list when there are none.

#### Scenario: Group of tickets
- **WHEN** the User has 3 Tickets for the event and 1 Ticket for another event
- **THEN** the 3 Tickets for the event are returned

#### Scenario: No tickets for the event
- **WHEN** the User has no Ticket for the event
- **THEN** an empty list is returned
