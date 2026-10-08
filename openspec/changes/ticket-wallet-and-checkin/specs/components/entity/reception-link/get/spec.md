# Spec Delta

## Purpose

Reads one ReceptionLink by its id.

## ADDED Requirements

### Requirement: Get returns the link

Get SHALL return the ReceptionLink with the given id, whatever its status, and SHALL fail with NotFound when no link has the id.

#### Scenario: Existing link

- **WHEN** a Revoked link is read by its id
- **THEN** it is returned with status Revoked

#### Scenario: Unknown link

- **WHEN** no link has the id
- **THEN** Get fails with NotFound
