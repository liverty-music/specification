## MODIFIED Requirements

### Requirement: Create merges into an existing slot

For each Concert, Create SHALL store a new Event when no Event exists at its Venue, date and start time (an unknown start matching only an unknown start). When one exists, Create SHALL keep that Event and its id, fill its start and open time only where they are unknown, never overwrite a known time, and add the Concert's performers to it. Concerts in one call that share a slot SHALL be stored once. When an Event with a publish state (an Organizer's Event) holds the slot of one of the Concerts, Create SHALL fail with FailedPrecondition and store nothing.

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

#### Scenario: Slot held by a first-party event
- **WHEN** a PUBLISHED Event of a first-party Series holds V on 2026-06-01 at 18:00 and a Concert of another Artist is created at that slot
- **THEN** Create fails with FailedPrecondition, the Event keeps its times and performers, and nothing is stored
