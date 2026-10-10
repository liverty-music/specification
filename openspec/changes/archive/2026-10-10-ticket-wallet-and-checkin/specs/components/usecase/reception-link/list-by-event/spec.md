# Spec Delta

## Purpose

ReceptionLinkUseCase.ListByEvent shows the owning organizer operator every ReceptionLink of one of their events and its state.

## ADDED Requirements

### Requirement: Owner sees the event's links

ListByEvent SHALL take the caller's Organizer and an event. It SHALL fail with PermissionDenied, without revealing whether the event exists, when Event.GetOrganizerID fails with NotFound or returns another Organizer. Otherwise it SHALL return ReceptionLink.ListByEvent for the event: each link's number, status, bound time and revoked time, and the token only for an Unused link.

#### Scenario: Links of an event

- **WHEN** the owner lists an event with link 1 (InUse since 14:10) and link 2 (Unused)
- **THEN** both are returned, 1 with bound time 14:10 and no token, 2 with its token

#### Scenario: Another organizer's event

- **WHEN** an operator lists the links of another Organizer's event
- **THEN** ListByEvent fails with PermissionDenied
