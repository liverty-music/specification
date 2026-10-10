# Spec Delta

## Purpose

Reads one TicketSale by its id, with its held count at a given time.

## ADDED Requirements

### Requirement: Get returns the sale and its held count

Get SHALL return the TicketSale with the given id, with its held count at the given time, and SHALL fail with NotFound when no TicketSale has the id.

#### Scenario: Sale with holds

- **WHEN** a sale whose Reservations hold 3 tickets at 18:00 is read at 18:00
- **THEN** the sale is returned with 3 held tickets

#### Scenario: Unknown sale

- **WHEN** no TicketSale has the id
- **THEN** Get fails with NotFound
