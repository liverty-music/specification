# Spec Delta

## Purpose

Reads one Dispute by its id, with its status and deadlines.

## ADDED Requirements

### Requirement: Dispute by id

Get SHALL return the Dispute with the given id and fail with NotFound when no Dispute has it.

#### Scenario: Stored dispute
- **WHEN** Get is called with the id of an Open Dispute
- **THEN** the Dispute is returned with its status Open and its evidence due time

#### Scenario: Unknown id
- **WHEN** no Dispute has the id
- **THEN** Get fails with NotFound
