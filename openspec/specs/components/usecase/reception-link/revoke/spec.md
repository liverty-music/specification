# components/usecase/reception-link/revoke Specification

## Purpose
ReceptionLinkUseCase.Revoke lets the owning organizer operator stop a ReceptionLink at once, for example when a device is lost or replaced.

## Requirements

### Requirement: Only the owner

Revoke SHALL take the caller's Organizer, a link and the current time. It SHALL read the link with ReceptionLink.Get and its event's Organizer with Event.GetOrganizerID, and SHALL fail with PermissionDenied, without revealing whether the link exists, when the link does not exist or its event is not owned by the caller's Organizer.

#### Scenario: Another organizer's link

- **WHEN** an operator revokes a link of another Organizer's event
- **THEN** Revoke fails with PermissionDenied and the link is unchanged

### Requirement: Revoked at once

Revoke SHALL revoke the link with ReceptionLink.Revoke and return it. From then on every call made through the link SHALL be refused, including a scan already sent but not yet decided. Revoking a link that is already Revoked SHALL return it unchanged.

#### Scenario: Device lost during the show

- **WHEN** the owner revokes the InUse link `受付1` at 19:10
- **THEN** `受付1` is Revoked and the next scan through it is refused

#### Scenario: Revoked twice

- **WHEN** the owner revokes a link that is already Revoked
- **THEN** it is returned unchanged
