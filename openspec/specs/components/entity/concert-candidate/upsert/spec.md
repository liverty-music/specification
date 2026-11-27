# ConcertCandidate.Upsert

## Purpose

Stages a discovered concert for review, or refreshes the pending ConcertCandidate that already stands for it.

## Requirements

### Requirement: One pending row per artist, date and venue

Upsert SHALL store a new ConcertCandidate unless one exists for the same Artist and date and the same resolved place id or, when the venue is unresolved, the same listed venue name. When one exists, Upsert SHALL refresh its series, title, times, admin area, source page, resolved place id and time zone, and SHALL keep its id and find time. Start time SHALL play no part in this match.

#### Scenario: First staging
- **WHEN** no ConcertCandidate exists for the Artist, date and place
- **THEN** a new ConcertCandidate is stored with the current find time

#### Scenario: Re-staged keeps queue position
- **WHEN** a ConcertCandidate for the same Artist, date and place was staged yesterday
- **THEN** it is refreshed and keeps yesterday's find time

#### Scenario: Other start time, same venue and date
- **WHEN** a ConcertCandidate starting 13:00 exists and one starting 18:00 for the same Artist, date and place is staged
- **THEN** the existing ConcertCandidate is refreshed to start at 18:00 and no second one is stored

### Requirement: Unknown artist

Upsert SHALL fail with FailedPrecondition when the Artist or Series does not exist.

#### Scenario: Unknown artist
- **WHEN** the ConcertCandidate names an Artist that does not exist
- **THEN** Upsert fails with FailedPrecondition
