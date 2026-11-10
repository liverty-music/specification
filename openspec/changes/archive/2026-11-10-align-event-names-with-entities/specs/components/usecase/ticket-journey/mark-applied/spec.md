## MODIFIED Requirements

### Requirement: Applied after every new lottery entry

MarkApplied SHALL run for each lottery entry announced as entered (LotteryEntry.Entered), with its Order's user and the event of its TicketStock. It SHALL read the entry with LotteryEntry.Get and record nothing when the entry is no longer Entered, because a drawn entry's announcement arrived late. Otherwise it SHALL record Applied, set by the platform, for the user's journey for the event through TicketJourney.UpsertIfReplaceable, so a journey at Unpaid or Paid stays as it is. Running it again for the same entry SHALL leave the journey as the first run left it. When UpsertIfReplaceable fails, MarkApplied SHALL fail with that error and is run again.

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
