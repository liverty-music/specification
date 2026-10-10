# Spec Delta

## Purpose

ScannerUseCase.Revoke lets the owning organizer operator stop a Scanner at once, for example when its device is lost or replaced.

## ADDED Requirements

### Requirement: Only the owner

Revoke SHALL take the caller's Organizer, a Scanner and the current time. It SHALL read the Scanner with Scanner.Get and its event's Organizer with Event.GetOrganizerID, and SHALL fail with PermissionDenied, without revealing whether the Scanner exists, when the Scanner does not exist or its event is not owned by the caller's Organizer.

#### Scenario: Another organizer's scanner

- **WHEN** an operator revokes a Scanner of another Organizer's event
- **THEN** Revoke fails with PermissionDenied and the Scanner is unchanged

### Requirement: Revoked at once

Revoke SHALL revoke the Scanner with Scanner.Revoke and return it. From then on every call made through the Scanner SHALL be refused, including a scan already sent but not yet decided. Revoking a Scanner that is already Revoked SHALL return it unchanged.

#### Scenario: Device lost during the show

- **WHEN** the owner revokes the InUse Scanner `受付1` at 19:10
- **THEN** `受付1` is Revoked and the next scan through it is refused

#### Scenario: Revoked twice

- **WHEN** the owner revokes a Scanner that is already Revoked
- **THEN** it is returned unchanged
