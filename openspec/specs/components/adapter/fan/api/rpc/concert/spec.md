# Concert RPC

## Purpose

The fan-facing concert service boundary: which concert calls need a signed-in fan, how the signed-in fan's home is supplied to the usecase, which requests are rejected before ConcertUseCase runs, and what a returned Concert carries.

## Requirements

### Requirement: Public concert calls need no sign-in

List, ListByArtists, ListByLocation and SearchNewConcerts SHALL be callable without sign-in. ListByFollower SHALL require a signed-in fan and fail with Unauthenticated otherwise.

#### Scenario: Guest lists concerts of chosen artists

- **WHEN** a caller who is not signed in calls ListByArtists with two artist ids and a home area
- **THEN** ConcertUseCase.ListByArtists runs and the grouped concerts are returned

#### Scenario: Guest asks for followed artists' concerts

- **WHEN** a caller who is not signed in calls ListByFollower
- **THEN** the call fails with Unauthenticated and no usecase runs

### Requirement: ListByFollower acts for the signed-in fan with their stored home

ListByFollower SHALL resolve the signed-in caller to their stored User (User.GetByExternalID) and call ConcertUseCase.ListByFollowerGrouped with that User, the User's stored Home and the optional from-date of the request; the request carries no fan and no home. When the caller has no stored account, the call SHALL fail with NotFound.

#### Scenario: Fan with a home

- **WHEN** a signed-in fan whose Home is JP-13 calls ListByFollower
- **THEN** the concerts of the fan's followed artists are grouped by proximity to JP-13

#### Scenario: Caller without an account

- **WHEN** the signed-in caller has no stored account
- **THEN** the call fails with NotFound

### Requirement: Concert requests are validated at the boundary

The boundary SHALL fail with InvalidArgument, before any usecase runs, when:
- List has no artist id;
- ListByArtists has fewer than 1 or more than 50 artist ids, or no home area;
- ListByLocation has no location, no from-date or no to-date, or a from-date later than its to-date (the limit on the length of the range belongs to ConcertUseCase.ListByLocation);
- SearchNewConcerts has no artist id.

#### Scenario: Too many artists

- **WHEN** ListByArtists is called with 51 artist ids
- **THEN** it fails with InvalidArgument

#### Scenario: Range backwards

- **WHEN** ListByLocation is called with from 2026-10-02 and to 2026-10-01
- **THEN** it fails with InvalidArgument

#### Scenario: Search without an artist

- **WHEN** SearchNewConcerts is called without an artist id
- **THEN** it fails with InvalidArgument and no search runs

### Requirement: What a returned concert carries

The Venue of every Concert returned by the fan boundary SHALL carry its id, name and admin area, and never its coordinates. A concert preview returned by SearchNewConcerts SHALL carry no Venue. When there are no concerts, List SHALL return an empty list, not NotFound.

#### Scenario: Venue without coordinates

- **WHEN** a returned Concert's Venue has known coordinates
- **THEN** the response carries the Venue's id, name and admin area and no coordinates

#### Scenario: Artist without concerts

- **WHEN** List is called for an artist with no concerts
- **THEN** it returns an empty list
