# LotterySalesPhase.Get

## Purpose

Returns one LotterySalesPhase by its id.

## Requirements

### Requirement: Get by id

Get SHALL return the phase with the given id and SHALL fail with NotFound when none exists.

#### Scenario: Existing phase

- **WHEN** Get is called with the id of a stored phase
- **THEN** that phase is returned

#### Scenario: Unknown id

- **WHEN** no phase has the id
- **THEN** Get fails with NotFound
