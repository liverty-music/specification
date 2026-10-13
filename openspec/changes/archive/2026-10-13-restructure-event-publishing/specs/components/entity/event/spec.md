# Spec Delta

## MODIFIED Requirements

### Requirement: Event identity is venue, date and start time

Two Events that are not DRAFT SHALL be the same performance exactly when they have the same Venue, the same local date and the same start time, where an unknown start time matches only another unknown start time. Series, performers and listed venue name SHALL play no part in identity. A DRAFT Event SHALL be the same performance as no other Event: it holds no slot, and any number of DRAFT Events and one Event that is not DRAFT can share a Venue, date and start time.

#### Scenario: Matinee and evening shows are distinct
- **WHEN** two Events share Venue and date and start at 13:00 and 18:00
- **THEN** they are different Events

#### Scenario: Same slot under different series is one event
- **WHEN** two Events share Venue, date and start time 18:00 but were grouped under different Series
- **THEN** they are the same Event

#### Scenario: Two unknown start times collapse
- **WHEN** two Events share Venue and date and neither has a start time
- **THEN** they are the same Event

#### Scenario: Unknown start does not match a known start
- **WHEN** two Events share Venue and date, one starting at 18:00 and one with no start time
- **THEN** they are different Events

#### Scenario: Draft beside a discovered event
- **WHEN** a DRAFT Event and a discovered Event share Venue, date and start time 18:00
- **THEN** they are different Events, and the discovered Event keeps the slot

## ADDED Requirements

### Requirement: Publish state of an event

An Event of a first-party Series SHALL have a publish state, DRAFT, PUBLISHED or CANCELLED, and an Event of a discovered Series SHALL have none. A new Event of a first-party Series SHALL start DRAFT. The only transitions SHALL be DRAFT to PUBLISHED and PUBLISHED to CANCELLED. A DRAFT Event SHALL NOT become CANCELLED; a DRAFT Event that will not happen is removed. CANCELLED SHALL be terminal.

#### Scenario: Discovered event has no publish state
- **WHEN** an Event belongs to a Series with no organizer
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

### Requirement: Public visibility

An Event SHALL be publicly visible when its Series is not first-party, or when it is PUBLISHED and its first-party Series' visibility is PUBLIC. A DRAFT or CANCELLED Event, and any Event of an UNLISTED Series, SHALL NOT be publicly visible.

#### Scenario: Discovered event is visible
- **WHEN** an Event's Series has no organizer
- **THEN** it is publicly visible

#### Scenario: Published event of a public series is visible
- **WHEN** an Event is PUBLISHED and its Series' visibility is PUBLIC
- **THEN** it is publicly visible

#### Scenario: Published event of an unlisted series is not visible
- **WHEN** an Event is PUBLISHED and its Series' visibility is UNLISTED
- **THEN** it is not publicly visible

#### Scenario: Draft date of a published tour is not visible
- **WHEN** a PUBLIC Series has one PUBLISHED Event and one DRAFT Event
- **THEN** only the PUBLISHED Event is publicly visible

#### Scenario: Cancelled date is not visible
- **WHEN** an Event is CANCELLED and its Series' visibility is PUBLIC
- **THEN** it is not publicly visible

### Requirement: What can change after publish

A DRAFT Event's Venue, local date, start time and open time SHALL be changeable. Once an Event is PUBLISHED, its Venue and local date SHALL NOT change; its open time SHALL be changeable; its start time SHALL be changeable, including from unknown to known, only while no TicketType offers the Event. A CANCELLED Event SHALL NOT change.

#### Scenario: Published venue is fixed
- **WHEN** an Event is PUBLISHED
- **THEN** its Venue and local date cannot change

#### Scenario: Doors-open time after publish
- **WHEN** an Event is PUBLISHED and a TicketType offers it
- **THEN** its open time can change

#### Scenario: Start time announced after publish
- **WHEN** an Event is PUBLISHED with no start time and no TicketType offers it
- **THEN** its start time can be set

#### Scenario: Start time on sale is fixed
- **WHEN** an Event is PUBLISHED and a TicketType offers it
- **THEN** its start time cannot change

#### Scenario: Cancelled event is fixed
- **WHEN** an Event is CANCELLED
- **THEN** none of its attributes can change
