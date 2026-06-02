## MODIFIED Requirements

### Requirement: Search Concerts by Artist

System must provide a way to search for future concerts of a specific artist using generative AI grounding. The system SHALL check the search log before calling the external API and skip the call when **either** a recent search exists **or** a new concert was recently discovered. The freshness window SHALL be configurable (default 24 hours) rather than fixed. The extracted concert data SHALL include the venue's administrative area (`admin_area`) when it can be determined with confidence. The `SearchNewConcerts` RPC SHALL be accessible without authentication to support guest onboarding flows.

#### Scenario: Successful Search

- **WHEN** `SearchNewConcerts` is called for an existing artist
- **AND** no search log exists, or the last search was longer ago than the configured freshness TTL
- **AND** no new concert was discovered for the artist within the configured discovery-skip window (default 14 days)
- **THEN** the system MUST call the external search API
- **AND** return a list of upcoming concerts found on the web
- **AND** each concert includes title, listed venue name, date, and optionally start time and `admin_area`
- **AND** results exclude concerts that are already stored in the database

#### Scenario: Skip search when recently searched

- **WHEN** `SearchNewConcerts` is called for an artist
- **AND** a search log exists with `searched_at` within the configured freshness TTL
- **THEN** the system MUST NOT call the external search API
- **AND** return an empty list

#### Scenario: Configurable freshness TTL per environment

- **WHEN** the freshness TTL is configured to 72 hours (e.g. in production) via the search-cache-TTL setting
- **AND** a search log exists with `searched_at` 50 hours ago
- **THEN** the system MUST treat the search as fresh and MUST NOT call the external API
- **AND** when the TTL is left unset, the system MUST default to 24 hours

#### Scenario: Skip search when recently discovered a new concert

- **WHEN** `SearchNewConcerts` is called for an artist
- **AND** the artist's search log records a `last_found_at` within the configured discovery-skip window (default 14 days)
- **THEN** the system MUST NOT call the external search API
- **AND** return an empty list
- **AND** this skip applies even if the last search itself is older than the freshness TTL

#### Scenario: Do not skip on discovery when never discovered

- **WHEN** `SearchNewConcerts` is called for an artist
- **AND** the artist's search log has no `last_found_at` recorded (null)
- **AND** no recent-search freshness skip applies
- **THEN** the discovery-recency check MUST NOT cause a skip
- **AND** the system MUST proceed to call the external search API

#### Scenario: Filter Past Events

- **WHEN** the search results include events with dates in the past
- **THEN** the system MUST filter them out and only return future events

#### Scenario: No Results

- **WHEN** no upcoming concerts are found for the artist
- **THEN** the system MUST return an empty list without error

#### Scenario: Missing Artist ID

- **WHEN** an `artist_id` is not provided
- **THEN** the system MUST return an `INVALID_ARGUMENT` error

#### Scenario: Unauthenticated access

- **WHEN** `SearchNewConcerts` is called without a bearer token
- **THEN** the system SHALL process the request normally (public procedure)
- **AND** the search log cache SHALL prevent abuse by skipping external API calls for recently searched or recently discovered artists
