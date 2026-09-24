# StagedConcert.Upsert

## Purpose

Stages a discovered concert for review, or refreshes the pending StagedConcert that already stands for it.

## Requirements

### Requirement: One pending row per artist, date and venue

Upsert SHALL store a new StagedConcert unless one exists for the same Artist and date and the same resolved place id or, when the venue is unresolved, the same listed venue name. When one exists, Upsert SHALL refresh its series, title, times, admin area, source page and resolved preview, and SHALL keep its id and discovered time. Start time SHALL play no part in this match.

#### Scenario: First staging
- **WHEN** no StagedConcert exists for the Artist, date and place
- **THEN** a new StagedConcert is stored with the current discovered time

#### Scenario: Re-staged keeps queue position
- **WHEN** a StagedConcert for the same Artist, date and place was staged yesterday
- **THEN** it is refreshed and keeps yesterday's discovered time

#### Scenario: Other start time, same venue and date
- **WHEN** a StagedConcert starting 13:00 exists and one starting 18:00 for the same Artist, date and place is staged
- **THEN** the existing StagedConcert is refreshed to start at 18:00 and no second one is stored

### Requirement: Unknown artist

Upsert SHALL fail with FailedPrecondition when the Artist or Series does not exist.

#### Scenario: Unknown artist
- **WHEN** the StagedConcert names an Artist that does not exist
- **THEN** Upsert fails with FailedPrecondition
