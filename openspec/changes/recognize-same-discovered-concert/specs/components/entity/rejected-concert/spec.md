## REMOVED Requirements

### Requirement: The log never suppresses

**Reason**: A duplicate whose venue cannot be resolved could not be settled while discovery ignored the log: each rejection was staged again by the next run.
**Migration**: Replaced by "Same listing", which SearchNewConcerts uses to leave out a listing identical to an entry.

## ADDED Requirements

### Requirement: Same listing

A found event SHALL be the same listing as a RejectedConcert entry when it is for the entry's Artist, on the entry's local date, at the same listed venue (see Venue, "Same listed venue") and at the same start time, two unknown start times counting as the same. Title, open time, admin area, time zone, source page, resolved place id and reason SHALL play no part.

#### Scenario: Identical listing
- **WHEN** an entry lists "【振替公演】仙台GIGS" on 2027-01-25 at 19:00 and an event is found for the same Artist with the same name, date and start time
- **THEN** the event is the same listing as the entry

#### Scenario: Name differs only in spacing or case
- **WHEN** an entry lists "Zepp Haneda" with no start time and an event is found for the same Artist on the same date listing "ZEPP HANEDA" with no start time
- **THEN** the event is the same listing as the entry

#### Scenario: Start time announced later
- **WHEN** an entry has no start time and an event is found for the same Artist, name and date starting at 18:00
- **THEN** the event is not the same listing

#### Scenario: Another venue
- **WHEN** an entry lists "Zepp Namba" and an event is found for the same Artist on the same date listing "Zepp Osaka Bayside"
- **THEN** the event is not the same listing

#### Scenario: Another Artist
- **WHEN** an event matches an entry in name, date and start time but is found for another Artist
- **THEN** the event is not the same listing
