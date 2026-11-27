## MODIFIED Requirements

### Requirement: Fill only unknown times

FillEventStartTimes SHALL set each given Event's start time and open time only where the Event's value is unknown; a known time SHALL never be overwritten, and an unknown supplied time leaves the Event unchanged. An unknown Event id SHALL be ignored, and an empty request SHALL change nothing. When filling a start time would give an Event the Venue, date and start time of another Event that is not DRAFT (see Event, "Event identity is venue, date and start time"), FillEventStartTimes SHALL fail with AlreadyExists and change none of the given Events.

#### Scenario: Unknown start filled
- **WHEN** an Event has no start time and 18:00 is supplied
- **THEN** the Event starts at 18:00

#### Scenario: Known start kept
- **WHEN** an Event starts at 18:00 and 19:00 is supplied
- **THEN** the Event still starts at 18:00

#### Scenario: Repeated fill
- **WHEN** the same fill is applied twice
- **THEN** the second application changes nothing

#### Scenario: Slot held by another event
- **WHEN** an Event at Venue V on 2026-12-19 has no start time, another Event at V on 2026-12-19 starts at 17:00, and 17:00 is supplied
- **THEN** FillEventStartTimes fails with AlreadyExists and the Event still has no start time
