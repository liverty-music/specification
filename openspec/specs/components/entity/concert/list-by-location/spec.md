# Concert.ListByLocation

## Purpose

Lists the candidate Concerts in a date range whose Venue could be HOME or NEARBY relative to a GeoLocation, each with its Venue including coordinates, for classification by the caller.

## Requirements

### Requirement: Candidates in range around a point

ListByLocation SHALL return every Concert dated from the first to the last given date inclusive whose Venue shares the GeoLocation's admin area or could lie within 200 km of its point, ordered by local date ascending, each with its Venue with coordinates when known. Concerts farther than 200 km can be among the candidates, but it SHALL NOT leave out any Concert in the same admin area or within 200 km. Concerts of a Series that is not publicly visible SHALL be left out.

#### Scenario: Same admin area without coordinates
- **WHEN** a Venue in the GeoLocation's admin area has no coordinates and hosts a Concert in the range
- **THEN** that Concert is returned

#### Scenario: Nearby venue in range
- **WHEN** a Venue 150 km from the point hosts a Concert in the range
- **THEN** that Concert is returned

#### Scenario: Outside the date range
- **WHEN** a Concert at a nearby Venue is dated the day after the range
- **THEN** it is not returned

#### Scenario: Nothing nearby
- **WHEN** no Concert in the range is in the admin area or near the point
- **THEN** ListByLocation returns an empty list
