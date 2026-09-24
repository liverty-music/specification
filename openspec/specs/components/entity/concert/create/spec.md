# Concert.Create

## Purpose

Stores one or more Concerts under Series that already exist, adding each as a new Event or merging it into the Event already at the same slot, and links their performers.

## Requirements

### Requirement: Create merges into an existing slot

For each Concert, Create SHALL store a new Event when no Event exists at its Venue, date and start time (an unknown start matching only an unknown start). When one exists, Create SHALL keep that Event and its id, fill its start and open time only where they are unknown, never overwrite a known time, and add the Concert's performers to it. Concerts in one call that share a slot SHALL be stored once.

#### Scenario: New slot
- **WHEN** no Event exists at Venue V on 2026-06-01 at 18:00
- **THEN** Create stores a new Event there with the Concert's performers

#### Scenario: Existing slot keeps its id
- **WHEN** an Event with id E exists at V on 2026-06-01 at 18:00 and a Concert with another id is created at that slot
- **THEN** Event E is kept and no second Event is stored

#### Scenario: Known open time is not overwritten
- **WHEN** the existing Event opens at 17:00 and the created Concert has no open time
- **THEN** the Event still opens at 17:00

#### Scenario: Unknown open time is filled
- **WHEN** the existing Event has no open time and the created Concert opens at 17:00
- **THEN** the Event opens at 17:00

#### Scenario: Different start time is a new event
- **WHEN** an Event exists at V on 2026-06-01 with no start time and a Concert starting at 18:00 is created there
- **THEN** a second Event starting at 18:00 is stored

### Requirement: Create reports newly announced concerts

Create SHALL return the ids of Events that are new, together with the ids of existing Events to which one of the Concerts' performers was newly added. An Event that already had every given performer SHALL NOT be returned. The returned ids SHALL be unique.

#### Scenario: Co-headliner found later
- **WHEN** Artist B is created at an existing Event where only Artist A performs
- **THEN** Create returns that Event's id

#### Scenario: Repeated create
- **WHEN** the same Concert with the same performer is created twice
- **THEN** the second Create returns no ids

### Requirement: Create is all or nothing

Create SHALL store all given Concerts and their performers together or none of them. It SHALL fail with InvalidArgument when a Concert has no id, no Venue, no Series or no performer, and with FailedPrecondition when a referenced Series, Venue or Artist does not exist.

#### Scenario: Unknown series
- **WHEN** one Concert refers to a Series that does not exist
- **THEN** Create fails with FailedPrecondition and stores nothing

#### Scenario: No performer
- **WHEN** a Concert has no performer
- **THEN** Create fails with InvalidArgument and stores nothing
