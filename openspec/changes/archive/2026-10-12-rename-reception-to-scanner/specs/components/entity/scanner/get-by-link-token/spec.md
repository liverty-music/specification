# Spec Delta

## Purpose

Finds the Scanner whose link token a device presents when it opens the link or scans.

## ADDED Requirements

### Requirement: GetByLinkToken returns the scanner that holds the link token

GetByLinkToken SHALL return the Scanner whose link token equals the given token, whatever its status, and SHALL fail with NotFound when no Scanner holds it. Comparing link tokens SHALL take the same time whatever the given token is.

#### Scenario: Known link token

- **WHEN** the link token of an Unused Scanner is given
- **THEN** that Scanner is returned

#### Scenario: Unknown link token

- **WHEN** no Scanner holds the link token
- **THEN** GetByLinkToken fails with NotFound
