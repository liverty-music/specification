## ADDED Requirements

### Requirement: Remove empty discovered Series created before a time

DeleteOrphaned SHALL remove every discovered Series (one without an Organizer) created before the given time that has no Event, no ConcertCandidate and no TicketSale, SHALL leave every other Series unchanged, and SHALL return how many it removed. A Series under which a concurrent change is still storing an Event, a ConcertCandidate or a TicketSale SHALL be left.

#### Scenario: Empty series removed
- **WHEN** a discovered Series created two days ago has no Event, no ConcertCandidate and no TicketSale, and DeleteOrphaned is given the time one day ago
- **THEN** it is removed

#### Scenario: Recent series kept
- **WHEN** an empty discovered Series was created an hour ago and DeleteOrphaned is given the time one day ago
- **THEN** it is kept

#### Scenario: Series with a concert candidate kept
- **WHEN** an old discovered Series has no Event but one ConcertCandidate
- **THEN** it is kept

#### Scenario: Series with a ticket sale kept
- **WHEN** an old discovered Series has no Event and no ConcertCandidate but one TicketSale
- **THEN** it is kept

#### Scenario: Series still being written
- **WHEN** a TicketSale is still being stored for an old discovered Series that has no Event
- **THEN** it is kept

#### Scenario: Organizer's series kept
- **WHEN** an Organizer's Series created two days ago has no Event
- **THEN** it is kept

## REMOVED Requirements

### Requirement: Remove only empty candidates

**Reason**: Removing a caller's given Series right after the caller emptied them raced with writes to those Series. DeleteOrphaned now removes Series by age.
**Migration**: Replaced by "Remove empty discovered Series created before a time"; the only caller is SeriesUseCase.RemoveEmptyDiscovered.
