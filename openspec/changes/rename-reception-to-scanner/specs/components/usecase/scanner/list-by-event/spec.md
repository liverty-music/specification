# Spec Delta

## Purpose

ScannerUseCase.ListByEvent shows the owning organizer operator every Scanner of one of their events and its state.

## ADDED Requirements

### Requirement: Owner sees the event's scanners

ListByEvent SHALL take the caller's Organizer and an event. It SHALL fail with PermissionDenied, without revealing whether the event exists, when Event.GetOrganizerID fails with NotFound or returns another Organizer. Otherwise it SHALL return Scanner.ListByEvent for the event: each Scanner's number, status, bound time and revoked time, and the link token only for an Unused Scanner.

#### Scenario: Scanners of an event

- **WHEN** the owner lists an event with Scanner 1 (InUse since 14:10) and Scanner 2 (Unused)
- **THEN** both are returned, 1 with bound time 14:10 and no link token, 2 with its link token

#### Scenario: Another organizer's event

- **WHEN** an operator lists the Scanners of another Organizer's event
- **THEN** ListByEvent fails with PermissionDenied
