# Spec Delta

## Purpose

ReceptionLinkUseCase.ListByEvent shows the owning organizer operator every ReceptionLink of one of their events and its state.

## ADDED Requirements

### Requirement: Owner sees the event's links

ListByEvent SHALL take the caller's Organizer and an event. It SHALL fail with PermissionDenied, without revealing whether the event exists, when Event.GetOrganizerID fails with NotFound or returns another Organizer. Otherwise it SHALL return ReceptionLink.ListByEvent for the event: each link's name, status, created time, bound time and revoked time, and the token only for an Unused link.

#### Scenario: Links of an event

- **WHEN** the owner lists an event with `受付A` (InUse since 14:10) and `受付B` (Unused)
- **THEN** both are returned, `受付A` with bound time 14:10 and no token, `受付B` with its token

#### Scenario: Another organizer's event

- **WHEN** an operator lists the links of another Organizer's event
- **THEN** ListByEvent fails with PermissionDenied
