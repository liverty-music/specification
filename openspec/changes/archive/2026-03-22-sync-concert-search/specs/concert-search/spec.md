## MODIFIED Requirements

### Requirement: Search Concerts by Artist

System must provide a way to search for future concerts of a specific artist using generative AI grounding. The system SHALL check the search log before calling the external API and skip the call if a recent search exists. The extracted concert data SHALL include the venue's administrative area (`admin_area`) when it can be determined with confidence. The `SearchNewConcerts` RPC SHALL be accessible without authentication to support guest onboarding flows. The RPC SHALL block until the search completes and return discovered concerts in the response.

#### Scenario: Successful Search

- **WHEN** `SearchNewConcerts` is called for an existing artist
- **AND** no search log exists or the last search was more than 24 hours ago
- **THEN** the system MUST call the external search API synchronously (blocking until completion)
- **AND** return discovered concerts in the `SearchNewConcertsResponse.concerts` field
- **AND** each concert includes title, listed venue name, date, and optionally start time and `admin_area`
- **AND** results exclude concerts that are already stored in the database

#### Scenario: Skip search when recently searched

- **WHEN** `SearchNewConcerts` is called for an artist
- **AND** a search log exists with `searched_at` within the last 24 hours
- **THEN** the system MUST NOT call the external search API
- **AND** return an empty `concerts` list

#### Scenario: Filter Past Events

- **WHEN** the search results include events with dates in the past
- **THEN** the system MUST filter them out and only return future events

#### Scenario: No Results

- **WHEN** no upcoming concerts are found for the artist
- **THEN** the system MUST return an empty `concerts` list without error

#### Scenario: Missing Artist ID

- **WHEN** an `artist_id` is not provided
- **THEN** the system MUST return an `INVALID_ARGUMENT` error

#### Scenario: Unauthenticated access

- **WHEN** `SearchNewConcerts` is called without a bearer token
- **THEN** the system SHALL process the request normally (public procedure)
- **AND** the search log cache SHALL prevent abuse by skipping external API calls for recently searched artists

#### Scenario: Search timeout

- **WHEN** the external search API does not respond within 60 seconds
- **THEN** the system SHALL return a deadline exceeded error
- **AND** the search log SHALL be marked as failed

## REMOVED Requirements

### Requirement: ListSearchStatuses RPC
**Reason**: Polling is no longer needed. SearchNewConcerts now blocks until completion and returns concerts directly.
**Migration**: Frontend removes all polling logic. Backend deletes ListSearchStatuses handler, usecase method, mapper, and related proto messages (ListSearchStatusesRequest, ListSearchStatusesResponse, ArtistSearchStatus, SearchStatus enum).
