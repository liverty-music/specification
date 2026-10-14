# Create

## Purpose

Create lets an organizer operator start a new first-party concert — a Series with one or more DRAFT Events and the Artists it represents as performers — that no fan can see and nobody is notified about until its Events are published.

## Requirements

### Requirement: Draft input is validated

Create SHALL fail with InvalidArgument, storing nothing, when the title is empty, when there is no event, when an event has no date, when an event's date is before the current UTC calendar day, or when an event's open time is after its start time. An empty performer list is accepted in a draft; publishing requires at least one performer.

#### Scenario: No event
- **WHEN** a draft is created with no event
- **THEN** Create fails with InvalidArgument

#### Scenario: Date in the past
- **WHEN** an event's date is yesterday in UTC
- **THEN** Create fails with InvalidArgument

#### Scenario: Doors after start
- **WHEN** an event opens at 19:00 and starts at 18:00
- **THEN** Create fails with InvalidArgument

### Requirement: Only represented artists

Create SHALL fail with PermissionDenied, without saying which Artist, when any performer is not among the Artists the caller's Organizer represents (Organizer.ListArtists).

#### Scenario: Unrepresented artist
- **WHEN** the draft names an Artist the Organizer does not represent
- **THEN** Create fails with PermissionDenied and stores nothing

### Requirement: Draft stored as DRAFT

Create SHALL store the Series, owned by the caller's Organizer, with one DRAFT Event per event — a multi-showtime day being several Events — each with the performers (Series.CreateDraft), and SHALL return the Series with its Events and performers (Series.GetAuthored). Nothing SHALL be announced.

#### Scenario: Draft for a represented artist
- **WHEN** an operator creates a draft with one event naming a represented Artist
- **THEN** a Series owned by the Organizer with one DRAFT Event is returned and no fan list or notification shows it

#### Scenario: Two showtimes
- **WHEN** the draft has 13:00 and 18:00 events on one date at one venue
- **THEN** the Series has two DRAFT Events

### Requirement: Each event's venue is a picked place

Every event SHALL give the place id of a place the operator picked from the map catalog; an event without one SHALL fail Create with InvalidArgument, storing nothing. For each event, Create SHALL use the Venue holding the place id when one is held (Venue.GetByPlaceID). Otherwise it SHALL read the place from the map catalog (Venue.GetPlace) and create a Venue with the place id and the place's name, coordinates and admin area (Venue.Create). When the catalog cannot be reached it SHALL fail with Unavailable, storing nothing; when the catalog has no such place it SHALL fail with InvalidArgument, storing nothing.

#### Scenario: Known place id
- **WHEN** an event gives a place id that a Venue holds
- **THEN** that Venue is used and the catalog is not read

#### Scenario: New place
- **WHEN** an event gives the place id of Zepp Haneda and no Venue holds it
- **THEN** a Venue for Zepp Haneda is created with that place id, its coordinates and the admin area JP-13

#### Scenario: Same name in two cities
- **WHEN** one event picks CLUB QUATTRO in Shibuya and another picks CLUB QUATTRO in Umeda
- **THEN** the two events have two different Venues, in JP-13 and JP-27

#### Scenario: Venue typed but not picked
- **WHEN** an event gives a venue name but no place id
- **THEN** Create fails with InvalidArgument and nothing is stored

#### Scenario: Catalog down for a new place
- **WHEN** no Venue holds the given place id and the catalog cannot be reached
- **THEN** Create fails with Unavailable and nothing is stored
