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

### Requirement: Centroid looked up when missing

When the supplied home area has no centroid, ListByArtists SHALL look it up from the home area's level-1 code. When the lookup fails or the code has no known centroid, the home area SHALL stay without a centroid, so only admin-area matches are HOME and everything else is AWAY.

#### Scenario: Home given by prefecture only
- **WHEN** the home area is JP-40 with no centroid
- **THEN** the centroid of JP-40 is used and a Concert 80 km away in JP-41 is NEARBY

#### Scenario: Unknown level-1 code
- **WHEN** the home area's level-1 code has no known centroid
- **THEN** Concerts outside that admin area are AWAY

#### Scenario: No home area
- **WHEN** no home area is supplied
- **THEN** every Concert is AWAY
