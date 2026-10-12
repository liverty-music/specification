# Spec Delta

## Purpose

Reads one Scanner by its id, whatever its status, for the Organizer's actions on it.

## ADDED Requirements

### Requirement: Get returns the scanner

Get SHALL return the Scanner with the given id, whatever its status, and SHALL fail with NotFound when no Scanner has the id.

#### Scenario: Existing scanner

- **WHEN** a Revoked Scanner is read by its id
- **THEN** it is returned with status Revoked

#### Scenario: Unknown scanner

- **WHEN** no Scanner has the id
- **THEN** Get fails with NotFound
