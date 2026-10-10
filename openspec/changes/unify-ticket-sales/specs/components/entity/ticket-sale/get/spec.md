# Spec Delta

## Purpose

Returns one TicketSale by its id, together with its TicketTypes.

## ADDED Requirements

### Requirement: Get by id

Get SHALL return the sale with the given id and all of its TicketTypes, and SHALL fail with NotFound when none exists.

#### Scenario: Existing sale
- **WHEN** Get is called with the id of a stored sale
- **THEN** that sale is returned with its TicketTypes

#### Scenario: Unknown id
- **WHEN** no sale has the id
- **THEN** Get fails with NotFound
