## MODIFIED Requirements

### Requirement: SetStatus records the fan's status

When a fan sets a status for an event, SetStatus SHALL record the given status, set by the fan, through TicketJourney.Upsert. It accepts any of the five journey statuses whatever the current status is and whoever set it. When TicketJourney.Upsert fails, SetStatus SHALL fail with that error.

#### Scenario: First status for an event

- **WHEN** the fan has no journey for the event and sets Tracking
- **THEN** the fan's journey for the event is recorded as Tracking set by the fan

#### Scenario: Changing an existing status

- **WHEN** the fan's journey for the event is Applied set by the platform and the fan sets Unpaid
- **THEN** the fan's journey for the event is recorded as Unpaid set by the fan

#### Scenario: Recording the status fails

- **WHEN** TicketJourney.Upsert fails with Unavailable
- **THEN** SetStatus fails with Unavailable and the journey stays as it was

## ADDED Requirements

### Requirement: SetStatus raises the hype level to match the concert

After recording Applied, Unpaid or Paid, SetStatus SHALL raise the fan's hype level for the concert's artist to the lowest hype level that matches the concert, through Follow.RaiseHype, when all of these hold: the event is a concert (Concert.ListByIDs); exactly one of the concert's artists is followed by the fan (Follow.ListByUser); and that Follow is raisable to that level. The fan's home comes from User.Get. Tracking and Lost SHALL raise nothing. A failure in any of these steps SHALL NOT fail SetStatus and SHALL NOT undo the recorded status.

#### Scenario: Applied for a distant concert

- **WHEN** a fan with home JP-13 who follows an artist at Nearby set by default sets Applied for the artist's concert in JP-40, whose proximity is Away
- **THEN** the Follow is at Away set by inference

#### Scenario: Level the fan set

- **WHEN** the fan's Follow of the artist is at Home set by the fan and the fan sets Paid for the artist's concert in JP-40
- **THEN** the Follow stays at Home set by the fan

#### Scenario: Concert already matched

- **WHEN** the fan's Follow is at Nearby set by default and the fan sets Applied for a concert whose proximity is Nearby
- **THEN** the Follow is unchanged

#### Scenario: Tracking raises nothing

- **WHEN** the fan sets Tracking for a distant concert of an artist at Nearby set by default
- **THEN** the Follow is unchanged

#### Scenario: Several followed artists perform

- **WHEN** the fan follows two of the concert's artists and sets Applied for the concert
- **THEN** neither Follow is changed

#### Scenario: Raising fails

- **WHEN** the status is recorded and Follow.RaiseHype fails
- **THEN** SetStatus succeeds and the new status stays recorded
