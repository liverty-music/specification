# Spec Delta

## Purpose

ReceptionLinkUseCase.Issue lets the owning organizer operator issue a named ReceptionLink for one of their published events, to hand to one reception device.

## ADDED Requirements

### Requirement: Only the owner of a published event

Issue SHALL take the caller's Organizer, an event and a name. It SHALL fail with PermissionDenied, without revealing whether the event exists, when Event.GetOrganizerID fails with NotFound or returns another Organizer. It SHALL fail with FailedPrecondition when Event.IsEventPublished reports false, or when Event.Get returns no start time, because such an event has no reception window.

#### Scenario: Another organizer's event

- **WHEN** an operator issues a link for an event owned by another Organizer
- **THEN** Issue fails with PermissionDenied and no link is created

#### Scenario: Draft event

- **WHEN** the owner issues a link for an event whose Series is DRAFT
- **THEN** Issue fails with FailedPrecondition

#### Scenario: Event without a start time

- **WHEN** the owner issues a link for a published event that has no start time
- **THEN** Issue fails with FailedPrecondition

### Requirement: Issued at any time before the event

Issue SHALL create the link with ReceptionLink.Create and return it with its token, whether or not the event's reception window has opened; an invalid or duplicate name fails as ReceptionLink.Create fails. The token returned here SHALL be the only time it is returned once the link has been bound.

#### Scenario: Link issued the day before

- **WHEN** the owner issues `受付A` on the day before the event
- **THEN** an Unused link `受付A` is returned with its token

#### Scenario: Duplicate name

- **WHEN** the event already has an InUse link `受付A` and the owner issues another `受付A`
- **THEN** Issue fails with AlreadyExists
