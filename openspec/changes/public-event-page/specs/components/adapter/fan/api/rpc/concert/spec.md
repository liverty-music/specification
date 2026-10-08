# Spec Delta

## MODIFIED Requirements

### Requirement: Public concert calls need no sign-in

Get, ListBySeries, List, ListByArtists, ListByLocation and SearchNewConcerts SHALL be callable without sign-in. ListByFollower SHALL require a signed-in fan and fail with Unauthenticated otherwise. Get SHALL call ConcertUseCase.Get and ListBySeries SHALL call ConcertUseCase.ListBySeries, each returning the usecase's result.

#### Scenario: Guest lists concerts of chosen artists

- **WHEN** a caller who is not signed in calls ListByArtists with two artist ids and a home area
- **THEN** ConcertUseCase.ListByArtists runs and the grouped concerts are returned

#### Scenario: Guest asks for followed artists' concerts

- **WHEN** a caller who is not signed in calls ListByFollower
- **THEN** the call fails with Unauthenticated and no usecase runs

#### Scenario: Guest opens an event page

- **WHEN** a caller who is not signed in calls Get with the id of an Event whose Series has an event page
- **THEN** ConcertUseCase.Get runs and the Concert is returned

#### Scenario: Guest lists the dates of a series

- **WHEN** a caller who is not signed in calls ListBySeries with the id of a Series that has an event page
- **THEN** ConcertUseCase.ListBySeries runs and the Series' Concerts are returned

### Requirement: Concert requests are validated at the boundary

The boundary SHALL fail with InvalidArgument, before any usecase runs, when:
- Get has no event id, or an event id that is not a UUID;
- ListBySeries has no series id, or a series id that is not a UUID;
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

#### Scenario: Event page without an id

- **WHEN** Get is called without an event id
- **THEN** it fails with InvalidArgument and no usecase runs

### Requirement: What a returned concert carries

The Venue of every Concert returned by the fan boundary SHALL carry its id, name and admin area, and never its coordinates. A concert preview returned by SearchNewConcerts SHALL carry no Venue. When there are no concerts, List SHALL return an empty list, not NotFound. The Series of every returned Concert SHALL carry the id of its Organizer when it is first-party, so the fan app can tell first-party concerts from discovered ones, and SHALL carry its description, cover image, visibility and publish state when it has them. A Series' share token SHALL never be returned.

#### Scenario: Venue without coordinates

- **WHEN** a returned Concert's Venue has known coordinates
- **THEN** the response carries the Venue's id, name and admin area and no coordinates

#### Scenario: Artist without concerts

- **WHEN** List is called for an artist with no concerts
- **THEN** it returns an empty list

#### Scenario: First-party concert in a list

- **WHEN** ListByFollower returns a Concert whose Series belongs to an Organizer
- **THEN** the Concert's Series carries that Organizer's id

#### Scenario: Discovered concert in a list

- **WHEN** ListByFollower returns a Concert whose Series has no organizer
- **THEN** the Concert's Series carries no Organizer id
