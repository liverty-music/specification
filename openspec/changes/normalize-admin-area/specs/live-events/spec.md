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

## ADDED Requirements

### Requirement: Dashboard Lane Classification

The dashboard SHALL classify live events into three lanes based on the geographic relationship between the event's venue and the user's home area.

#### Scenario: Home lane assignment

- **WHEN** a live event's `venue.admin_area` equals the user's `home` value (ISO 3166-2 code comparison)
- **THEN** the event SHALL be assigned to the `home` lane

#### Scenario: Nearby lane assignment

- **WHEN** a live event's `venue.admin_area` is set (non-null)
- **AND** it does not equal the user's `home` value
- **THEN** the event SHALL be assigned to the `nearby` lane

#### Scenario: Away lane assignment

- **WHEN** a live event's `venue.admin_area` is not set (null/absent)
- **THEN** the event SHALL be assigned to the `away` lane

#### Scenario: User has no home set

- **WHEN** the user has not set a home area
- **AND** a live event has a non-null `venue.admin_area`
- **THEN** the event SHALL be assigned to the `nearby` lane

### Requirement: ISO 3166-2 Display Conversion

The frontend SHALL convert ISO 3166-2 codes to human-readable names for display, using the browser's locale for language selection.

#### Scenario: Display admin_area in venue detail

- **WHEN** a venue's `admin_area` ISO 3166-2 code is displayed to the user
- **THEN** the frontend SHALL render the localized name (e.g., `JP-13` → "東京都" for `ja`, "Tokyo" for `en`)

#### Scenario: Display home area in region setup

- **WHEN** the region setup sheet presents area options to the user
- **THEN** the options SHALL display localized names
- **AND** the selected value sent to the backend SHALL be the ISO 3166-2 code
