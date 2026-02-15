## MODIFIED Requirements

### Requirement: Search Concerts by Artist

System must provide a way to search for future concerts of a specific artist using generative AI grounding. The system SHALL check the search log before calling the external API and skip the call if a recent search exists.

#### Scenario: Successful Search

- **WHEN** `SearchNewConcerts` is called for an existing artist
- **AND** no search log exists or the last search was more than 24 hours ago
- **THEN** the system MUST call the external search API
- **AND** return a list of upcoming concerts found on the web
- **AND** each concert includes title, venue, date, and start time
- **AND** results exclude concerts that are already stored in the database

#### Scenario: Skip search when recently searched

- **WHEN** `SearchNewConcerts` is called for an artist
- **AND** a search log exists with `searched_at` within the last 24 hours
- **THEN** the system MUST NOT call the external search API
- **AND** return an empty list

#### Scenario: Filter Past Events

- **WHEN** the search results include events with dates in the past
- **THEN** the system MUST filter them out and only return future events

#### Scenario: No Results

- **WHEN** no upcoming concerts are found for the artist
- **THEN** the system MUST return an empty list without error

#### Scenario: Missing Artist ID

- **WHEN** an `artist_id` is not provided
- **THEN** the system MUST return an `INVALID_ARGUMENT` error
