# Spec Delta

## Purpose

Returns one TicketType by its id, together with the TicketSale that offers it.

## ADDED Requirements

### Requirement: Get by id

Get SHALL return the TicketType with the given id and its TicketSale, and SHALL fail with NotFound when none exists.

#### Scenario: Existing ticket type
- **WHEN** Get is called with the id of a stored TicketType
- **THEN** that TicketType is returned with its sale

#### Scenario: Unknown id
- **WHEN** no TicketType has the id
- **THEN** Get fails with NotFound
