# Spec Delta

## Purpose

Returns one TicketType by its id, together with the TicketSale that offers it and, for a first-come TicketType, its held count at a given time.

## ADDED Requirements

### Requirement: Get by id

Get SHALL return the TicketType with the given id and its TicketSale, a TicketType of a FirstCome sale with its held count at the given time, and SHALL fail with NotFound when none exists.

#### Scenario: Existing ticket type
- **WHEN** Get is called with the id of a stored TicketType
- **THEN** that TicketType is returned with its sale

#### Scenario: First-come ticket type with holds
- **WHEN** a first-come TicketType whose Checkouts hold 3 tickets at 18:00 is read at 18:00
- **THEN** it is returned with 3 held tickets

#### Scenario: Unknown id
- **WHEN** no TicketType has the id
- **THEN** Get fails with NotFound
