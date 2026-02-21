## MODIFIED Requirements

### Requirement: Concert Schedue Data Model

The system MUST define standard data structures for core concert entities to ensure consistency across services.

#### Scenario: Artist Definition

- **WHEN** an artist is represented
- **THEN** it MUST include a unique ID, name, and a list of official media channels.

#### Scenario: Venue Definition

- **WHEN** a venue is represented
- **THEN** it MUST include a unique ID and name.
- **AND** it MAY include an administrative area (`admin_area`) representing the prefecture or region.

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

## ADDED Requirements

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
