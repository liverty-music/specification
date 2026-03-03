# Capability: Concert Search

## Purpose

To define the interface and behavior for discovering new concerts for artists, enabling the system to keep its concert catalog up-to-date.

## Requirements

### Requirement: Search Concerts by Artist

System must provide a way to search for future concerts of a specific artist using generative AI grounding. The system SHALL check the search log before calling the external API and skip the call if a recent search exists. The extracted concert data SHALL include the venue's administrative area (`admin_area`) when it can be determined with confidence. The `SearchNewConcerts` RPC SHALL be accessible without authentication to support guest onboarding flows.

#### Scenario: Successful Search

- **WHEN** `SearchNewConcerts` is called for an existing artist
- **AND** no search log exists or the last search was more than 24 hours ago
- **THEN** the system MUST call the external search API
- **AND** return a list of upcoming concerts found on the web
- **AND** each concert includes title, listed venue name, date, start time, and optionally `admin_area`
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

#### Scenario: Unauthenticated access

- **WHEN** `SearchNewConcerts` is called without a bearer token
- **THEN** the system SHALL process the request normally (public procedure)
- **AND** the search log cache SHALL prevent abuse by skipping external API calls for recently searched artists

### Requirement: Venue Administrative Area Extraction

The Gemini extraction pipeline SHALL attempt to identify the administrative area (都道府県 / state / province) of each venue. Accuracy is prioritized over coverage — an incorrect value is strictly forbidden.

#### Scenario: AdminArea explicitly stated in source

- **WHEN** the source page or venue name explicitly includes the prefecture or state
- **THEN** the extracted `admin_area` SHALL contain that value (e.g., `"大阪府"`, `"California"`)

#### Scenario: AdminArea unambiguously inferable from venue name

- **WHEN** the venue name unambiguously implies a known administrative area (e.g., "Zepp Nagoya" → "愛知県", "札幌ドーム" → "北海道")
- **THEN** the extracted `admin_area` SHALL contain the inferred value

#### Scenario: AdminArea uncertain or ambiguous

- **WHEN** the administrative area cannot be determined with confidence from the source text
- **THEN** `admin_area` SHALL be omitted (empty string / `NULL`)
- **AND** the system SHALL NOT guess or infer from partial information

### Requirement: Resilient External Search

The system SHALL retry transient failures from the external search API using exponential backoff before reporting an error. The `SearchNewConcerts` RPC SHALL have a dedicated timeout (≥15 seconds) independent of the global handler timeout to accommodate the latency of AI-grounded search.

#### Scenario: Transient Gemini timeout is retried

- **WHEN** `SearchNewConcerts` calls the external search API
- **AND** the API returns a transient error (504 Gateway Timeout, 503 Unavailable, 429 Too Many Requests, or 499 Client Cancelled)
- **THEN** the system MUST retry the call up to 2 additional times with exponential backoff
- **AND** return results if any retry succeeds

#### Scenario: All retries exhausted

- **WHEN** `SearchNewConcerts` calls the external search API
- **AND** all retry attempts fail with transient errors
- **THEN** the system MUST return an error to the caller
- **AND** log each failed attempt with the error details

#### Scenario: Non-transient error is not retried

- **WHEN** `SearchNewConcerts` calls the external search API
- **AND** the API returns a non-transient error (400 Bad Request, 401 Unauthorized)
- **THEN** the system MUST NOT retry the call
- **AND** return the error immediately
