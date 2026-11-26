# Spec Delta

## ADDED Requirements

### Requirement: A lost entry marks the fan's journey Lost

When a fan's lottery entry is lost because it was not drawn or because the card could not be charged, and no other lottery entry of the fan for the event is Entered or Won, TicketJourneyUseCase.MarkLost SHALL record the fan's ticket journey for the event as Lost, set by the platform, so the Timetable and the concert sheet show Lost without the fan setting it.

#### Scenario: Loss shown on the Timetable

- **WHEN** a fan whose only entry for the event is not drawn opens the Timetable after the draw
- **THEN** the event's journey shows Lost

#### Scenario: Cancelled concert

- **WHEN** a fan's entry ends because the concert was cancelled
- **THEN** the event's journey is as it was before the cancellation
