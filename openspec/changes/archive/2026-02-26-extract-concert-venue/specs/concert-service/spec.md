## MODIFIED Requirements

### Requirement: Concert Persistence

The system SHALL automatically persist any new concerts discovered via the search mechanism. The `ConcertRepository.Create` method SHALL accept a variadic number of concerts for bulk insert support.

#### Scenario: Persist New Concerts

- **WHEN** `SearchNewConcerts` is called and finds concerts not currently in the database
- **THEN** the new concerts are saved to the persisted storage via a single bulk insert call
- **AND** returned in the response with valid IDs

#### Scenario: Persist Venues

- **WHEN** a discovered concert has a venue that does not exist in the database
- **THEN** a new venue is created dynamically based on the listed venue name provided by the source
- **AND** if an `admin_area` was extracted for the concert, it SHALL be stored on the venue record
- **AND** the new concert is associated with this new venue

#### Scenario: Single concert creation

- **WHEN** `Create` is called with a single concert argument
- **THEN** it SHALL behave identically to the previous single-insert implementation

## ADDED Requirements

### Requirement: Listed Venue Name Preservation

The system SHALL preserve the raw venue name as found on the artist's official site on the Event record, separate from the normalized `Venue.Name`. This ensures the original source text is available for future normalization workflows (e.g., matching against Google Maps or MusicBrainz).

#### Scenario: Listed venue name stored on event creation

- **WHEN** a new concert event is persisted
- **THEN** the `listed_venue_name` field on the event SHALL contain the exact venue name string returned by the Gemini extraction

#### Scenario: Listed venue name is non-empty for discovered concerts

- **WHEN** Gemini returns a non-empty venue string for a concert
- **THEN** `listed_venue_name` on the persisted event SHALL be that string

### Requirement: Venue AdminArea Persistence

The system SHALL store the administrative area extracted by Gemini on the Venue record when available.

#### Scenario: AdminArea stored on new venue creation

- **WHEN** a new venue is created and the scraped concert includes a non-empty `admin_area`
- **THEN** the venue record SHALL have `admin_area` set to that value

#### Scenario: AdminArea is NULL when not extracted

- **WHEN** a new venue is created and the scraped concert has no `admin_area` (empty or absent)
- **THEN** the venue record SHALL have `admin_area` set to `NULL`
