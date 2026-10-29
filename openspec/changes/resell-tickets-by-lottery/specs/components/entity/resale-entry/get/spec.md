# Spec Delta

## Purpose

Reads one ResaleEntry with its Order, in any state, so a usecase can check who owns it and where it stands.

## ADDED Requirements

### Requirement: Get an entry

Get SHALL return the ResaleEntry with the given id and its Order, in any state, and SHALL fail with NotFound when none has the id.

#### Scenario: Existing entry
- **WHEN** a Lapsed entry is read by its id
- **THEN** it is returned with its Order

#### Scenario: Unknown id
- **WHEN** no entry has the id
- **THEN** Get fails with NotFound
