# Spec Delta

## Purpose

ScannerUseCase.Create lets the owning organizer operator create a Scanner for one of their published events, to hand to one device of the venue staff.

## ADDED Requirements

### Requirement: Only the owner of a published event

Create SHALL take the caller's Organizer and an event. It SHALL fail with PermissionDenied, without revealing whether the event exists, when Event.GetOrganizerID fails with NotFound or returns another Organizer. It SHALL fail with FailedPrecondition when Event.IsEventPublished reports false, or when Event.Get returns no start time, because such an event has no admission window.

#### Scenario: Another organizer's event

- **WHEN** an operator creates a Scanner for an event owned by another Organizer
- **THEN** Create fails with PermissionDenied and no Scanner is created

#### Scenario: Draft event

- **WHEN** the owner creates a Scanner for an event whose Series is DRAFT
- **THEN** Create fails with FailedPrecondition

#### Scenario: Event without a start time

- **WHEN** the owner creates a Scanner for a published event that has no start time
- **THEN** Create fails with FailedPrecondition

### Requirement: Created at any time before the event

Create SHALL create the Scanner with Scanner.Create and return it with its link token, whether or not the event's admission window has opened. The link token returned here SHALL be the only time it is returned once the Scanner has been bound.

#### Scenario: Scanner created the day before

- **WHEN** the owner creates the event's first Scanner on the day before the event
- **THEN** an Unused Scanner 1 is returned with its link token
