# Spec Delta

## Purpose

Returns one LotteryEntry by its id, in any state.

## ADDED Requirements

### Requirement: Get by id

Get SHALL return the entry with the given id, including a Withdrawn one, and SHALL fail with NotFound when none exists.

#### Scenario: Existing entry

- **WHEN** Get is called with the id of a stored entry
- **THEN** that entry is returned

#### Scenario: Unknown id

- **WHEN** no entry has the id
- **THEN** Get fails with NotFound
