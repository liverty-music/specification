## ADDED Requirements

### Requirement: The reference area names a first-level Area

ListByLocation SHALL take an area code and a date range; the caller supplies no point. It SHALL resolve the area code (Area.Resolve, without a country) and fail with InvalidArgument, reading no Concert, when Area.Resolve fails with NotFound or returns an Area whose code differs from the given area code. Otherwise the reference point SHALL be a GeoLocation whose admin area is the Area's code and whose point is the Area's reference point, with no point when the Area has none.

#### Scenario: Prefecture code
- **WHEN** ListByLocation is called with the area JP-13
- **THEN** the Concerts are read and grouped relative to the Area JP-13 and its reference point

#### Scenario: Territory code
- **WHEN** ListByLocation is called with the area HK
- **THEN** the Concerts are read and grouped relative to the Area HK

#### Scenario: Well-formed code that is no Area
- **WHEN** ListByLocation is called with the area JP-99
- **THEN** ListByLocation fails with InvalidArgument and no Concert is read

#### Scenario: Lower-level code
- **WHEN** ListByLocation is called with the area FR-33, which resolves to FR-NAQ
- **THEN** ListByLocation fails with InvalidArgument and no Concert is read

## MODIFIED Requirements

### Requirement: HOME and NEARBY only

ListByLocation SHALL read the candidate Concerts for the reference point and range (Concert.ListByLocation), group them by date and proximity to the reference point (Concert.GroupByDateAndProximity), drop every AWAY Concert, and drop every date left with no HOME or NEARBY Concert. Groups SHALL be in date order. When the Area has no reference point, only the Concerts in its admin area SHALL be returned, all as HOME.

#### Scenario: Same admin area far away
- **WHEN** a Concert's venue is in the requested Area 300 km from its reference point
- **THEN** it is returned as HOME

#### Scenario: Other admin area within 200 km
- **WHEN** a Concert's venue is in another admin area 150 km from the reference point
- **THEN** it is returned as NEARBY

#### Scenario: Beyond 200 km in another admin area
- **WHEN** a Concert's venue is in another admin area 250 km from the reference point
- **THEN** it is not returned

#### Scenario: Area without a reference point
- **WHEN** the requested Area has no reference point, and Concerts in the range are at a Venue in that Area and at a Venue in another Area 30 km away
- **THEN** only the Concert in the requested Area is returned, as HOME

#### Scenario: Date with only far concerts
- **WHEN** every Concert on a date is AWAY
- **THEN** that date is not returned

#### Scenario: Nothing nearby
- **WHEN** no Concert in the range is HOME or NEARBY
- **THEN** no groups are returned, without error
