# Order.Get

## Purpose

Returns one Order by its id.

## Requirements

### Requirement: Get by id

Get SHALL return the Order with the given id and SHALL fail with NotFound when none exists.

#### Scenario: Existing order

- **WHEN** Get is called with the id of a stored Order
- **THEN** that Order is returned

#### Scenario: Unknown id

- **WHEN** no Order has the id
- **THEN** Get fails with NotFound
