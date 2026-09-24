# Settlement.ListHeld

## Purpose

Lists the Settlements still Held, with their splits.

## Requirements

### Requirement: Held settlements

ListHeld SHALL return every Held Settlement with its splits, oldest first, and no Released or Reversed Settlement. It SHALL return an empty list when none is Held.

#### Scenario: Mixed statuses

- **WHEN** one Settlement is Held and one is Released
- **THEN** only the Held Settlement is returned

#### Scenario: None held

- **WHEN** no Settlement is Held
- **THEN** an empty list is returned
