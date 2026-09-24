# Settlement.GetByOrderID

## Purpose

Returns the Settlement of one Order.

## Requirements

### Requirement: Settlement of an order

GetByOrderID SHALL return the Order's Settlement with its splits and SHALL fail with NotFound when the Order has none.

#### Scenario: Settlement exists

- **WHEN** the Order has a Settlement
- **THEN** it is returned with its splits

#### Scenario: No settlement

- **WHEN** the Order has no Settlement
- **THEN** GetByOrderID fails with NotFound
