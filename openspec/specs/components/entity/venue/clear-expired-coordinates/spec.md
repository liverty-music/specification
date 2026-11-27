# components/entity/venue/clear-expired-coordinates Specification

## Purpose
Removes every Venue's cached coordinates once they are more than 28 days old, so that with a daily run map catalog content is never kept past the 30 days it may be stored.

## Requirements

### Requirement: Remove coordinates fetched more than 28 days ago

ClearExpiredCoordinates SHALL take an instant and remove the coordinates and fetch time of every Venue whose coordinates were fetched more than 28 days before it. It SHALL leave every other Venue, and every other attribute of a cleared Venue, the place id included, unchanged. Running it again with the same instant SHALL change nothing more.

#### Scenario: Expired coordinates removed
- **WHEN** a Venue's coordinates were fetched at 2026-10-20 04:00 UTC and the instant is 2026-11-24 04:00 UTC
- **THEN** the Venue has no coordinates and no fetch time and keeps its place id

#### Scenario: Recent coordinates kept
- **WHEN** a Venue's coordinates were fetched at 2026-10-30 04:00 UTC and the instant is 2026-11-24 04:00 UTC
- **THEN** the Venue keeps its coordinates and fetch time

#### Scenario: Nothing expired
- **WHEN** no Venue has coordinates fetched more than 28 days before the instant
- **THEN** no Venue changes
