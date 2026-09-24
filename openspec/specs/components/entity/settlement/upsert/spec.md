# Settlement.Upsert

## Purpose

Stores a Settlement for an Order unless one already exists, and returns the Order's Settlement.

## Requirements

### Requirement: One settlement per order

Upsert SHALL store the given Settlement when its Order has none and return it; when the Order already has a Settlement, Upsert SHALL store nothing new and return the existing one.

#### Scenario: First settlement

- **WHEN** Upsert is called for an Order without a Settlement
- **THEN** the Settlement is stored and returned

#### Scenario: Settlement exists

- **WHEN** the Order already has a Settlement
- **THEN** the existing Settlement is returned and no second one is stored
