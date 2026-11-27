## MODIFIED Requirements

### Requirement: ListFollowed acts for the signed-in fan with their stored home

ListFollowed SHALL resolve the signed-in caller to their stored User (User.GetByProviderUserID) and call ConcertUseCase.ListFollowed with that User, the User's stored Home and the optional from-date of the request; the request carries no fan and no home. Without a from-date, the call SHALL return the Concerts on or after the current date at each Concert's Venue, so a client asks for the default upcoming view by leaving the from-date out, not by sending its device's date. When the caller has no stored account, the call SHALL fail with NotFound.

#### Scenario: Fan with a home

- **WHEN** a signed-in fan whose Home is JP-13 calls ListFollowed
- **THEN** the concerts of the fan's followed artists are grouped by proximity to JP-13

#### Scenario: Upcoming view without a from-date

- **WHEN** a signed-in fan calls ListFollowed without a from-date at 2027-03-15 08:00 in Asia/Tokyo (2027-03-14 23:00 in Europe/London), and followed artists play on 2027-03-14 at a Venue in `JP-13` and at a Venue in `GB-ENG`
- **THEN** the concert in `GB-ENG` is returned and the concert in `JP-13` is not

#### Scenario: Caller without an account

- **WHEN** the signed-in caller has no stored account
- **THEN** the call fails with NotFound

### Requirement: Concert requests are validated before the usecase runs

The boundary SHALL fail with InvalidArgument, before any usecase runs, when:
- Get has no event id, or an event id that is not a UUID;
- ListBySeries has no series id, or a series id that is not a UUID;
- ListByArtist has no artist id;
- ListByArtists has fewer than 1 or more than 50 artist ids, or no home area;
- ListByLocation has no area, an area not in the form of a first-level Area code (two uppercase letters, optionally followed by a hyphen and 1 to 3 uppercase letters or digits), no from-date or no to-date, or a from-date later than its to-date (the limit on the length of the range, and whether the area is a first-level Area, belong to ConcertUseCase.ListByLocation).

#### Scenario: Too many artists

- **WHEN** ListByArtists is called with 51 artist ids
- **THEN** it fails with InvalidArgument

#### Scenario: Range backwards

- **WHEN** ListByLocation is called with from 2026-10-02 and to 2026-10-01
- **THEN** it fails with InvalidArgument

#### Scenario: Concert page without an id

- **WHEN** Get is called without an event id
- **THEN** it fails with InvalidArgument and no usecase runs

#### Scenario: Location search without an area

- **WHEN** ListByLocation is called with a date range and no area
- **THEN** it fails with InvalidArgument and no usecase runs

#### Scenario: Free-text area

- **WHEN** ListByLocation is called with the area "Tokyo"
- **THEN** it fails with InvalidArgument and no usecase runs

### Requirement: What a returned concert carries

Every response of the fan concert service that returns Concerts SHALL also return, once each, every Series and every Artist those Concerts refer to; a Concert carries only the id of its Series (through its Event) and the ids of its Artists. Every returned Event SHALL carry its local date and, when known, its open and start times as times of day at its Venue, never as instants. Every returned Venue SHALL carry its id, name, admin area and time zone, and never its coordinates, so an Event's date and times are read in its Venue's time zone. When there are no concerts, ListByArtist SHALL return an empty list, not NotFound. Every returned Series SHALL carry its Organizer when it is first-party, so the fan app can tell first-party concerts from discovered ones and show who sells the tickets: the Organizer's id, name and, when present, business details (legal name, representative name, business address, business phone number and contact email), which the checkout shows as the 特商法 (Specified Commercial Transactions Act) disclosure, and never its platform fee rate. Every returned Series SHALL carry its description, cover image, visibility and publish state when it has them, on every call alike. A Series' share token SHALL never be returned.

#### Scenario: Venue without coordinates

- **WHEN** a returned Concert's Venue has known coordinates
- **THEN** the response carries the Venue's id, name, admin area and time zone and no coordinates

#### Scenario: Concert abroad

- **WHEN** a returned Concert is on 2027-03-14 at a Venue in `KR-11` with the time zone `Asia/Seoul`, opening at 17:30 and starting at 18:30 local time
- **THEN** the Event carries the local date 2027-03-14, the open time 17:30 and the start time 18:30, and its Venue carries the time zone `Asia/Seoul`

#### Scenario: Start time unknown

- **WHEN** a returned Concert's Event has no known start time
- **THEN** the Event carries its local date and no start time

#### Scenario: Artist without concerts

- **WHEN** ListByArtist is called for an artist with no concerts
- **THEN** it returns an empty list

#### Scenario: First-party concert in a list

- **WHEN** ListFollowed returns a Concert whose Series belongs to an Organizer
- **THEN** the Series returned with it carries that Organizer's id

#### Scenario: Discovered concert in a list

- **WHEN** ListFollowed returns a Concert whose Series has no Organizer
- **THEN** the Series returned with it carries no Organizer id

#### Scenario: Tour in one list

- **WHEN** ListFollowed returns three Concerts of one Series, all performed by the same Artist
- **THEN** the response carries that Series once and that Artist once

#### Scenario: Cover image in a list

- **WHEN** ListByArtists returns a Concert whose first-party Series has a cover image
- **THEN** the Series returned with it carries the cover image, as Get does

#### Scenario: Organizer shown for a first-party concert

- **WHEN** Get returns a Concert whose Series belongs to an Organizer with business details and a platform fee rate
- **THEN** the Series returned with it carries the Organizer's id, name and business details, and no platform fee rate

## ADDED Requirements

### Requirement: ListByLocation passes the requested area

ListByLocation SHALL call ConcertUseCase.ListByLocation with the area code and the date range of the request; the request carries no point, and the reference point is the one the usecase resolves for the area. A failure of the usecase, InvalidArgument for an area that is no first-level Area included, SHALL be returned unchanged.

#### Scenario: Guest searches near a prefecture

- **WHEN** a caller who is not signed in calls ListByLocation with the area `JP-13` and a 7-day range
- **THEN** ConcertUseCase.ListByLocation runs for `JP-13` and that range, and its groups are returned

#### Scenario: Area that is no first-level Area

- **WHEN** ListByLocation is called with the area `JP-99`
- **THEN** ConcertUseCase.ListByLocation fails with InvalidArgument and ListByLocation returns it
