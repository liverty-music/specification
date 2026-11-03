# components/usecase/ticket-journey/mark-applied Specification

## Purpose
TicketJourneyUseCase.MarkApplied sets a fan's ticket journey for an event to Applied once their lottery entry on the platform is made, outside the entry's own transaction, so a failure here never fails or undoes the entry.

## Requirements

### Requirement: Applied after every new lottery entry

MarkApplied SHALL run for each lottery entry announced as new, with its Order's user and the event of its TicketStock. It SHALL read the entry with LotteryEntry.Get and record nothing when the entry is no longer Entered, because a drawn entry's announcement arrived late. Otherwise it SHALL record Applied, set by the platform, for the user's journey for the event through TicketJourney.UpsertIfReplaceable, so a journey at Unpaid or Paid stays as it is. Running it again for the same entry SHALL leave the journey as the first run left it. When UpsertIfReplaceable fails, MarkApplied SHALL fail with that error and is run again.

#### Scenario: Fan enters a lottery

- **WHEN** a new entry of a fan with no journey for the event is announced
- **THEN** the fan's journey for the event is Applied set by the platform

#### Scenario: Fan was tracking the event

- **WHEN** a new entry is announced for a fan whose journey for the event is Tracking set by inference
- **THEN** the journey is Applied set by the platform

#### Scenario: Announcement arrives after the purchase

- **WHEN** a new entry is announced after the fan's journey for the event became Paid set by the platform
- **THEN** the journey stays Paid set by the platform

#### Scenario: Announcement arrives after the draw

- **WHEN** a new entry is announced after the draw made it Lost and the fan set their journey to Lost
- **THEN** the journey stays Lost set by the fan

#### Scenario: Recording fails

- **WHEN** TicketJourney.UpsertIfReplaceable fails with Unavailable
- **THEN** MarkApplied fails and the journey is Applied when it runs again

### Requirement: MarkApplied raises the hype level to match the concert

After it records Applied, MarkApplied SHALL raise the fan's hype level for the concert's artist to the lowest hype level that matches the concert, through Follow.RaiseHype, when all of these hold: the event is a concert (Concert.ListByIDs); the concert has a lowest matching hype level (components/entity/follow); exactly one of the concert's artists is followed by the fan (Follow.ListByUser); and that Follow is raisable to that level. The fan's home comes from User.Get. When MarkApplied recorded nothing, it SHALL raise nothing. A failure in any of these steps SHALL NOT fail MarkApplied, and MarkApplied SHALL NOT be run again for it.

#### Scenario: Entry for a distant concert

- **WHEN** a new entry is announced for a fan with home JP-13 who follows the artist at Nearby set by default, for the artist's concert in JP-40, whose proximity is Away
- **THEN** the journey is Applied set by the platform and the Follow is at Away set by inference

#### Scenario: Raising fails

- **WHEN** Applied is recorded and Follow.RaiseHype fails
- **THEN** MarkApplied succeeds and is not run again
