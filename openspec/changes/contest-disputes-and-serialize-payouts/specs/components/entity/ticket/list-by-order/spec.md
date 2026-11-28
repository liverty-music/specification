# Spec Delta

## Purpose

Lists the Tickets one Order issued, in any status, with their admit times.

## ADDED Requirements

### Requirement: Tickets of an order

ListByOrder SHALL return every Ticket the given Order issued, Issued or Voided, oldest issue time first, each with its status, issue time and admit time. It SHALL return an empty list when the Order issued none or does not exist.

#### Scenario: One ticket admitted, one resold
- **WHEN** an Order issued two Tickets, one admitted and one Voided by a resale
- **THEN** both are returned, the admitted one with its admit time

#### Scenario: Order without tickets
- **WHEN** the Order is Pending
- **THEN** an empty list is returned
