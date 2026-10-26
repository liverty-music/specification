## MODIFIED Requirements

### Requirement: A new start time takes its slot

When the start time of a given PUBLISHED Event changes, the Event SHALL take the slot at its Venue, date and new start time, keeping its id:
- when no Event that is not DRAFT is at that slot, the start time is simply set, whether or not a SuppressedConcert matches the slot;
- when an Event of a discovered Series is at that slot, that Event SHALL be merged into this one: fans tracking it track this Event instead, its performers are added to this Event's Concert, and it is removed;
- when an Event of any other first-party Series is at that slot, Update SHALL fail with FailedPrecondition and change nothing.

#### Scenario: Start time announced
- **WHEN** a PUBLISHED Event with no start time is given the start time 18:00 and no Event is at that slot
- **THEN** the Event starts at 18:00 and keeps its id

#### Scenario: Discovered event at the new slot
- **WHEN** a PUBLISHED Event E is given 18:00 and a discovered Event D that fans track is at E's Venue and date at 18:00
- **THEN** E starts at 18:00 with its id kept, those fans track E, and D is gone

#### Scenario: Suppressed new slot
- **WHEN** the new slot of a PUBLISHED Event matches a SuppressedConcert and no Event is at that slot
- **THEN** the Event takes the new start time and keeps its id

#### Scenario: First-party event at the new slot
- **WHEN** the new slot of a PUBLISHED Event holds an Event of another first-party Series
- **THEN** Update fails with FailedPrecondition and nothing changes
