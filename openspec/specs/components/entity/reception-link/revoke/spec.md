# components/entity/reception-link/revoke Specification

## Purpose
Revokes a ReceptionLink so it can no longer be used.

## Requirements

### Requirement: Revoke ends the link

Revoke SHALL take a ReceptionLink and a time. When the link is Unused or InUse it SHALL make it Revoked with that revoked time. When it is already Revoked it SHALL change nothing. It SHALL fail with NotFound when no link has the id.

#### Scenario: Link in use

- **WHEN** an InUse link is revoked at 18:05
- **THEN** it is Revoked with revoked time 18:05

#### Scenario: Already revoked

- **WHEN** a link revoked at 18:05 is revoked again at 18:10
- **THEN** its revoked time stays 18:05

#### Scenario: Unknown link

- **WHEN** no link has the id
- **THEN** Revoke fails with NotFound
