# Spec Delta

## Purpose

Sets the state of one LotteryEntry; it changes no other attribute.

## ADDED Requirements

### Requirement: Update the state

UpdateState SHALL set the entry's state to the given state and SHALL fail with NotFound when no entry has the id.

#### Scenario: State changed

- **WHEN** UpdateState sets an Entered entry to Withdrawn
- **THEN** the entry's state is Withdrawn and its other attributes are unchanged

#### Scenario: Unknown id

- **WHEN** no entry has the id
- **THEN** UpdateState fails with NotFound
