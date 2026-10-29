# Spec Delta

## Purpose

Reads one TicketStock by its id with its SeatType and, at a given time, its sold count and held count.

## ADDED Requirements

### Requirement: Get by id

Get SHALL return the TicketStock with the given id with its SeatType and, at the given time, its sold count and its held count, and SHALL fail with NotFound when no TicketStock has the id.

#### Scenario: Stock with holds
- **WHEN** a TicketStock of 150 with 100 sold and Checkouts holding 3 tickets at 18:00 is read at 18:00
- **THEN** it is returned with its SeatType, a sold count of 100 and a held count of 3

#### Scenario: Unknown id
- **WHEN** no TicketStock has the id
- **THEN** Get fails with NotFound
