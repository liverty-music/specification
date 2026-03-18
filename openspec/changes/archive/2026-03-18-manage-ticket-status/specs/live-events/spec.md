## MODIFIED Requirements

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

#### Scenario: Concert card displays ticket journey badge

- **WHEN** a concert is rendered on the dashboard
- **AND** the user has a ticket journey for that concert's event
- **THEN** the concert card SHALL display a badge indicating the current `TicketJourneyStatus`

#### Scenario: Concert card without ticket journey

- **WHEN** a concert is rendered on the dashboard
- **AND** the user has no ticket journey for that concert's event
- **THEN** the concert card SHALL NOT display a journey status badge
