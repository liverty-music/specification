## MODIFIED Requirements

### Requirement: Public concert calls need no sign-in

Get, ListBySeries, List, ListByArtists and ListByLocation SHALL be callable without sign-in. ListByFollower SHALL require a signed-in fan and fail with Unauthenticated otherwise. Get SHALL call ConcertUseCase.Get and ListBySeries SHALL call ConcertUseCase.ListBySeries, each returning the usecase's result.

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

### Requirement: What a returned concert carries

Every response of the fan concert service that returns Concerts SHALL also return, once each, every Series and every Artist those Concerts refer to; a Concert carries only the id of its Series (through its Event) and the ids of its Artists. Every returned Venue SHALL carry its id, name and admin area, and never its coordinates. When there are no concerts, List SHALL return an empty list, not NotFound. Every returned Series SHALL carry the id of its Organizer when it is first-party, so the fan app can tell first-party concerts from discovered ones, and SHALL carry its description, cover image, visibility and publish state when it has them, on every call alike. A Series' share token SHALL never be returned.

#### Scenario: Venue without coordinates

- **WHEN** a returned Concert's Venue has known coordinates
- **THEN** the response carries the Venue's id, name and admin area and no coordinates

#### Scenario: Artist without concerts

- **WHEN** List is called for an artist with no concerts
- **THEN** it returns an empty list

#### Scenario: First-party concert in a list

- **WHEN** ListByFollower returns a Concert whose Series belongs to an Organizer
- **THEN** the Series returned with it carries that Organizer's id

#### Scenario: Discovered concert in a list

- **WHEN** ListByFollower returns a Concert whose Series has no organizer
- **THEN** the Series returned with it carries no Organizer id

#### Scenario: Tour in one list

- **WHEN** ListByFollower returns three Concerts of one Series, all performed by the same Artist
- **THEN** the response carries that Series once and that Artist once

#### Scenario: Cover image in a list

- **WHEN** ListByArtists returns a Concert whose first-party Series has a cover image
- **THEN** the Series returned with it carries the cover image, as Get does

## REMOVED Requirements

### Requirement: Concert requests are validated at the boundary

**Reason**: SearchNewConcerts leaves the fan concert service, so its validation rule and the scenario "Search without an artist" go with it.

**Migration**: The remaining rules move unchanged to "Concert requests are validated before the usecase runs" below.

## ADDED Requirements

### Requirement: Concert requests are validated before the usecase runs

The boundary SHALL fail with InvalidArgument, before any usecase runs, when:
- Get has no event id, or an event id that is not a UUID;
- ListBySeries has no series id, or a series id that is not a UUID;
- List has no artist id;
- ListByArtists has fewer than 1 or more than 50 artist ids, or no home area;
- ListByLocation has no location, no from-date or no to-date, or a from-date later than its to-date (the limit on the length of the range belongs to ConcertUseCase.ListByLocation).

#### Scenario: Too many artists

- **WHEN** ListByArtists is called with 51 artist ids
- **THEN** it fails with InvalidArgument

#### Scenario: Range backwards

- **WHEN** ListByLocation is called with from 2026-10-02 and to 2026-10-01
- **THEN** it fails with InvalidArgument

#### Scenario: Event page without an id

- **WHEN** Get is called without an event id
- **THEN** it fails with InvalidArgument and no usecase runs
