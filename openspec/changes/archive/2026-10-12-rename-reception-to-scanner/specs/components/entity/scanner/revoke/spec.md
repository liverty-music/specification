# Spec Delta

## Purpose

Revokes a Scanner so that no call through its link is accepted any more.

## ADDED Requirements

### Requirement: Revoke ends the scanner

Revoke SHALL take a Scanner and a time. When the Scanner is Unused or InUse it SHALL make it Revoked with that revoked time. When it is already Revoked it SHALL change nothing. It SHALL fail with NotFound when no Scanner has the id.

#### Scenario: Scanner in use

- **WHEN** an InUse Scanner is revoked at 18:05
- **THEN** it is Revoked with revoked time 18:05

#### Scenario: Already revoked

- **WHEN** a Scanner revoked at 18:05 is revoked again at 18:10
- **THEN** its revoked time stays 18:05

#### Scenario: Unknown scanner

- **WHEN** no Scanner has the id
- **THEN** Revoke fails with NotFound
