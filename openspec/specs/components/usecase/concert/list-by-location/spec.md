# List By Location

## Purpose

ListByLocation gives any caller every Concert, over a date range of at most 30 days, whose Venue lies in the reference point's administrative area or within 200 km of it, grouped by date into HOME and NEARBY. Dates with no such Concert are left out.

## Requirements

### Requirement: Range of at most 30 days

ListByLocation SHALL fail with InvalidArgument when the last date is more than 30 days after the first. Ranges in the past SHALL be allowed.

#### Scenario: 31-day range
- **WHEN** the range is 2026-08-01 to 2026-09-01
- **THEN** ListByLocation fails with InvalidArgument

#### Scenario: Past range
- **WHEN** the range is last week
- **THEN** Concerts of last week are considered

### Requirement: HOME and NEARBY only

ListByLocation SHALL read the candidate Concerts for the GeoLocation and range (Concert.ListByLocation), group them by date and proximity to the GeoLocation (Concert.GroupByDateAndProximity), drop every AWAY Concert, and drop every date left with no HOME or NEARBY Concert. Groups SHALL be in date order.

#### Scenario: Same admin area far away
- **WHEN** a Concert's venue is in the GeoLocation's admin area 300 km from the point
- **THEN** it is returned as HOME

#### Scenario: Other admin area within 200 km
- **WHEN** a Concert's venue is in another admin area 150 km from the point
- **THEN** it is returned as NEARBY

#### Scenario: Beyond 200 km in another admin area
- **WHEN** a Concert's venue is in another admin area 250 km from the point
- **THEN** it is not returned

#### Scenario: Date with only far concerts
- **WHEN** every Concert on a date is AWAY
- **THEN** that date is not returned

#### Scenario: Nothing nearby
- **WHEN** no Concert in the range is HOME or NEARBY
- **THEN** no groups are returned, without error
