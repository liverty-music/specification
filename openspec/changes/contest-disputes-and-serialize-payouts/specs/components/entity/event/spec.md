# Spec Delta

## MODIFIED Requirements

### Requirement: Publish state of an event

An Event of a first-party Series SHALL have a publish state, DRAFT, PUBLISHED or CANCELLED, and an Event of a discovered Series SHALL have none. A new Event of a first-party Series SHALL start DRAFT. The only transitions SHALL be DRAFT to PUBLISHED and PUBLISHED to CANCELLED, the latter only while the Event is cancellable. A DRAFT Event SHALL NOT become CANCELLED; a DRAFT Event that will not happen is removed. CANCELLED SHALL be terminal.

#### Scenario: Discovered event has no publish state
- **WHEN** an Event belongs to a Series with no Organizer
- **THEN** it has no publish state

#### Scenario: New authored event is a draft
- **WHEN** an Event is added to a first-party Series
- **THEN** it is DRAFT

#### Scenario: Draft is not cancellable
- **WHEN** an Event is DRAFT
- **THEN** it cannot become CANCELLED

#### Scenario: Cancelled stays cancelled
- **WHEN** an Event is CANCELLED
- **THEN** it has no transition to DRAFT or PUBLISHED

## ADDED Requirements

### Requirement: Cancellable until 24 hours after its start

An Event's cancellation limit SHALL be its current start time plus 24 hours; an Event with no start time has none. An Event SHALL be cancellable at an instant when it is PUBLISHED and the instant is before its cancellation limit, or it has none. A concert stopped midway can still be cancelled the next morning; from 24 hours after its start it is a concert that took place and SHALL NOT become CANCELLED.

#### Scenario: Stopped midway, recorded the next morning
- **WHEN** a PUBLISHED Event that started at 18:00 on 2026-12-05 is checked at 09:00 on 2026-12-06
- **THEN** it is cancellable

#### Scenario: 24 hours after the start
- **WHEN** the same Event is checked at 18:00 on 2026-12-06
- **THEN** it is not cancellable

#### Scenario: Start time not known
- **WHEN** a PUBLISHED Event with no start time is checked
- **THEN** it is cancellable

#### Scenario: Draft
- **WHEN** a DRAFT Event is checked before its date
- **THEN** it is not cancellable
