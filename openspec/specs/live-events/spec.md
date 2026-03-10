# live-events Specification

## Purpose

The `live-events` capability defines the core domain entities—Artists, Venues, and Concerts—and the standard interfaces for managing them. It establishes the single source of truth for concert metadata, enabling consistent data representation and access across the platform's crawler, backend services, and frontend applications.

## Requirements

### Requirement: Concert Schedue Data Model

The system MUST define standard data structures for core concert entities to ensure consistency across services.

#### Scenario: Artist Definition

- **WHEN** an artist is represented
- **THEN** it MUST include a unique ID, name, and a list of official media channels.

#### Scenario: Venue Definition

- **WHEN** a venue is represented
- **THEN** it MUST include a unique ID and name.
- **AND** it MAY include an administrative area (`admin_area`) as an ISO 3166-2 subdivision code representing the venue's geographic administrative division (e.g., `JP-13` for Tokyo, `JP-40` for Fukuoka).

#### Scenario: Concert Definition

- **WHEN** a concert is represented
- **THEN** it MUST include the artist ID, venue ID, local date (`local_date`), title, and start time.
- **AND** it MAY include open time, source URL, listed venue name, and an embedded `Venue` object.
- **AND** all primitive scalar fields (date, time, title, URL, venue name) SHALL be represented as VO wrapper messages.

#### Scenario: Event Definition

- **WHEN** an event is represented
- **THEN** it MUST include a unique ID, an embedded `Venue` object, title, and local date.
- **AND** it MAY include start time, open time, and merkle root.
- **AND** all primitive scalar fields SHALL be represented as VO wrapper messages.
- **AND** it SHALL NOT include `create_time` or `update_time` fields.

### Requirement: Artist Management

The system MUST provide an interface to manage artists and their media links.

#### Scenario: Create Artist

- **WHEN** `CreateArtist` is called with a name
- **THEN** the system MUST create a new Artist entity and return it.

#### Scenario: List Artists

- **WHEN** `ListArtists` is called
- **THEN** the system MUST return a list of all registered artists.

#### Scenario: Add Media

- **WHEN** `CreateArtistMedia` is called with an artist ID, media type, and URL
- **THEN** the system MUST associate the media with the artist.

#### Scenario: Remove Media

- **WHEN** `DeleteArtistMedia` is called with a media ID
- **THEN** the system MUST remove the media association.

### Requirement: Live Schedule Access

The system MUST provide access to the collected schedule of concerts.

#### Scenario: List Concerts

- **WHEN** `ListConcerts` is called for a valid artist ID
- **THEN** the system MUST return a chronologically sorted list of future concerts for that artist.

#### Scenario: List Concerts by Follower

- **WHEN** `ListByFollower` is called by an authenticated user
- **THEN** the system MUST return concerts for all artists followed by that user, grouped by date and classified into home/nearby/away lanes
- **AND** each group SHALL contain a calendar date and three concert lists (home, nearby, away)
- **AND** groups SHALL be ordered by date ascending
- **AND** lane classification SHALL be performed by the backend using the proximity classification model
- **AND** the result SHALL be retrieved in a single RPC call

### Requirement: Proto Value Object Consistency

All primitive scalar fields on `Concert` and `Event` proto messages SHALL use VO wrapper messages to carry validation constraints and semantic meaning, matching the Go entity layer conventions.

#### Scenario: LocalDate VO

- **WHEN** a calendar date is represented in `Concert` or `Event`
- **THEN** it SHALL use the `LocalDate` wrapper message containing a `google.type.Date` value.
- **AND** the field SHALL be named `local_date`.

#### Scenario: StartTime and OpenTime VOs

- **WHEN** a start or open time is represented in `Concert` or `Event`
- **THEN** it SHALL use `StartTime` or `OpenTime` wrapper messages containing a `google.protobuf.Timestamp` value.

#### Scenario: Title VO

- **WHEN** a title is represented in `Concert` or `Event`
- **THEN** it SHALL use the `Title` wrapper message containing a non-empty string value.

#### Scenario: SourceUrl VO

- **WHEN** a source URL is represented in `Concert`
- **THEN** it SHALL use the `SourceUrl` wrapper message containing a URI-validated string value.

#### Scenario: ListedVenueName VO

- **WHEN** a raw scraped venue name is represented in `Concert`
- **THEN** it SHALL use the `ListedVenueName` wrapper message containing a string value.

### Requirement: Venue Embedding in Concert and Event

Both `Concert` and `Event` proto messages SHALL embed a resolved `Venue` object populated by the server, rather than relying solely on a `venue_id` reference.

#### Scenario: Concert carries embedded Venue

- **WHEN** a `Concert` is returned from any RPC
- **THEN** the `venue` field SHALL be populated with the corresponding `Venue` entity including `name` and `admin_area` if available.

#### Scenario: Event carries embedded Venue

- **WHEN** an `Event` is returned from any RPC
- **THEN** the `venue` field SHALL be populated with the corresponding `Venue` entity.

### Requirement: Go Entity Field Name Alignment

The Go domain entity `event.Event.LocalEventDate` SHALL be renamed to `LocalDate` to align with the proto VO field name.

#### Scenario: LocalEventDate renamed to LocalDate

- **WHEN** the Go `entity.Event` struct is used in backend code
- **THEN** the date field SHALL be accessed as `LocalDate` (not `LocalEventDate`).

### Requirement: Dashboard Lane Classification

The backend SHALL classify live events into three lanes based on the proximity classification model, replacing the previous frontend-only classification.

#### Scenario: Home lane assignment

- **WHEN** a concert's venue `admin_area` matches the user's `home.level_1`
- **THEN** the concert SHALL be placed in the `home` list of its date group

#### Scenario: Nearby lane assignment

- **WHEN** a concert's venue has coordinates within 200km of the user's home centroid
- **AND** the venue `admin_area` does not match the user's `home.level_1`
- **THEN** the concert SHALL be placed in the `nearby` list of its date group

#### Scenario: Away lane assignment

- **WHEN** a concert's venue is beyond 200km, has no coordinates, or the user has no home set
- **THEN** the concert SHALL be placed in the `away` list of its date group

#### Scenario: User has no home set

- **WHEN** the user has not set a home area
- **THEN** all concerts SHALL be placed in the `away` list of their respective date groups

### Requirement: ISO 3166-2 Display Conversion

The frontend SHALL convert ISO 3166-2 codes to human-readable names for display, using the browser's locale for language selection.

#### Scenario: Display admin_area in venue detail

- **WHEN** a venue's `admin_area` ISO 3166-2 code is displayed to the user
- **THEN** the frontend SHALL render the localized name (e.g., `JP-13` → "東京都" for `ja`, "Tokyo" for `en`)

#### Scenario: Display home area in region setup

- **WHEN** the region setup sheet presents area options to the user
- **THEN** the options SHALL display localized names
- **AND** the selected value sent to the backend SHALL be structured as a `Home` message with `country_code` and `level_1`

### Requirement: Live Event Availability Check

The system SHALL provide a mechanism to check whether an artist has upcoming live events by querying the `ConcertService/List` RPC. This replaces the previous hash-based mock implementation.

#### Scenario: Artist has upcoming events

- **WHEN** `checkLiveEvents` is called with an artist ID
- **AND** `ConcertService/List` returns one or more concerts for that artist
- **THEN** the system SHALL return `true`

#### Scenario: Artist has no upcoming events

- **WHEN** `checkLiveEvents` is called with an artist ID
- **AND** `ConcertService/List` returns an empty list
- **THEN** the system SHALL return `false`

#### Scenario: Concert list call fails

- **WHEN** `checkLiveEvents` is called with an artist ID
- **AND** the `ConcertService/List` RPC call fails
- **THEN** the system SHALL return `false`
- **AND** the system SHALL log the error
