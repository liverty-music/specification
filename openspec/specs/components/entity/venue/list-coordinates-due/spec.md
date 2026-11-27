# components/entity/venue/list-coordinates-due Specification

## Purpose
Lists the Venues whose cached coordinates are missing or due for a refresh from the map catalog, the held ones oldest first, so a daily run can refresh them before they expire.

## Requirements

### Requirement: Venues with a place id whose coordinates are missing or older than 20 days

ListCoordinatesDue SHALL take an instant and a maximum count and return each Venue that has a place id and whose coordinates are missing or were fetched more than 20 days before the instant, with its id and place id. Venues with coordinates SHALL come first, by fetch time, oldest first, then Venues without coordinates; at most the maximum count SHALL be returned. It SHALL return an empty list when no Venue is due, and SHALL fail with InvalidArgument when the maximum count is below 1.

#### Scenario: Coordinates older than 20 days
- **WHEN** a Venue with a place id has coordinates fetched at 2026-11-03 04:00 UTC and the instant is 2026-11-24 04:00 UTC
- **THEN** it is returned

#### Scenario: Coordinates younger than 20 days
- **WHEN** a Venue with a place id has coordinates fetched at 2026-11-05 04:00 UTC and the instant is 2026-11-24 04:00 UTC
- **THEN** it is not returned

#### Scenario: Missing coordinates
- **WHEN** a Venue has a place id and no coordinates
- **THEN** it is returned, after every due Venue that has coordinates

#### Scenario: No place id
- **WHEN** a Venue has no place id
- **THEN** it is not returned

#### Scenario: More due than the maximum
- **WHEN** 3 Venues are due, fetched 25, 23 and 21 days before the instant, and the maximum count is 2
- **THEN** the Venues fetched 25 and 23 days before are returned, in that order

#### Scenario: Nothing due
- **WHEN** every Venue with a place id has coordinates fetched in the last 20 days
- **THEN** an empty list is returned
