## ADDED Requirements

### Requirement: Track Concert Search History

The system SHALL maintain a log of when each artist's concerts were last searched via external sources. The log is keyed by artist ID and records the timestamp of the most recent search.

#### Scenario: Record search after Gemini call

- **WHEN** `SearchNewConcerts` completes a Gemini API call for an artist
- **THEN** the system MUST upsert a record in `latest_search_logs` with the artist's ID and the current timestamp

#### Scenario: First search for an artist

- **WHEN** no search log exists for the given artist
- **THEN** the system MUST insert a new record with the current timestamp

#### Scenario: Subsequent search for an artist

- **WHEN** a search log already exists for the given artist
- **THEN** the system MUST update the existing record's `searched_at` to the current timestamp
