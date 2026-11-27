# List By Artists

## Purpose

ListByArtists gives any caller, signed in or not, the Concerts of chosen Artists, grouped by date and sorted into HOME, NEARBY and AWAY relative to a home area the caller supplies.

## Requirements

### Requirement: Chosen artists' concerts in proximity groups

ListByArtists SHALL read the Artists' Concerts (Concert.ListByArtists) — past and upcoming — and return them as proximity groups relative to the supplied home area (Concert.GroupByDateAndProximity), in date order. No Concerts SHALL yield no groups.

#### Scenario: Concerts across two dates
- **WHEN** the chosen Artists have Concerts on two dates
- **THEN** two proximity groups are returned, earlier date first

#### Scenario: No concerts
- **WHEN** none of the chosen Artists has a Concert
- **THEN** no groups are returned, without error

### Requirement: The home's reference point is its Area's

ListByArtists SHALL resolve the supplied home area's level-1 code (Area.Resolve) and classify the Concerts relative to a home area whose centroid is the returned Area's reference point. When Area.Resolve fails with NotFound or InvalidArgument, when it returns an Area whose code differs from the level-1 code, or when the Area has no reference point, the home area SHALL have no centroid, so only admin-area matches are HOME and everything else is AWAY; ListByArtists SHALL NOT fail for it. Any other failure of Area.Resolve SHALL fail ListByArtists.

#### Scenario: Home given by prefecture only
- **WHEN** the home area is JP-40
- **THEN** the reference point of the Area JP-40 is used and a Concert 80 km away in JP-41 is NEARBY

#### Scenario: Overseas home
- **WHEN** the home area is US-CA and the Area US-CA has a reference point
- **THEN** that reference point is used and a Concert 150 km away in US-NV is NEARBY

#### Scenario: Area without a reference point
- **WHEN** the home area's Area has no reference point
- **THEN** Concerts in that admin area are HOME and every other Concert is AWAY

#### Scenario: Code that is no first-level Area
- **WHEN** the home area's level-1 code is JP-99
- **THEN** Concerts outside that admin area are AWAY and ListByArtists does not fail

#### Scenario: No home area
- **WHEN** no home area is supplied
- **THEN** every Concert is AWAY
