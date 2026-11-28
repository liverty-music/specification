# Spec Delta

## Purpose

Lists every Dispute of one Order, so a caller can tell whether its payment is disputed now.

## ADDED Requirements

### Requirement: Disputes of an order

ListByOrder SHALL return every Dispute of the given Order, oldest open time first, in any status. It SHALL return an empty list when the Order has none or does not exist.

#### Scenario: One won and one open
- **WHEN** an Order has a Won Dispute and an Open Dispute
- **THEN** both are returned, the older first

#### Scenario: Never disputed
- **WHEN** an Order has no Dispute
- **THEN** an empty list is returned
