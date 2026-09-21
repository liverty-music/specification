<!-- merge_group: SEARCH-LOG | target: components/usecase/concert/search-new-concerts | members: 2 -->
<!-- renamed_scenarios: 0 -->

### Requirement: Track Concert Search History and Last Discovery Time

The system SHALL maintain a log of when each artist's concerts were last searched via external sources. The log is keyed by artist ID and records the timestamp of the most recent search (`searched_at`) in `latest_search_logs`. The system SHALL also record, per artist, the timestamp at which a search most recently discovered at least one genuinely new concert (`last_found_at`); this timestamp drives the discovery-recency skip in concert search and is distinct from `searched_at` (which records every search attempt, productive or not).

#### Scenario: Record search after Gemini call

- **WHEN** `SearchNewConcerts` completes a Gemini API call for an artist
- **THEN** the system MUST upsert a record in `latest_search_logs` with the artist's ID and the current timestamp

#### Scenario: First search for an artist

- **WHEN** no search log exists for the given artist
- **THEN** the system MUST insert a new record with the current timestamp

#### Scenario: Subsequent search for an artist

- **WHEN** a search log already exists for the given artist
- **THEN** the system MUST update the existing record's `searched_at` to the current timestamp

#### Scenario: Record discovery when new concerts are published

- **WHEN** a search for an artist produces one or more new concerts after deduplication (i.e. a `concert.discovered` event is published)
- **THEN** the system MUST set the artist's `last_found_at` to the current timestamp in `latest_search_logs`

#### Scenario: Do not record discovery when nothing new is found

- **WHEN** a search for an artist completes but yields no new concerts after deduplication
- **THEN** the system MUST NOT modify the artist's `last_found_at`
- **AND** the existing `last_found_at` value (if any) MUST be preserved

#### Scenario: Never discovered

- **WHEN** an artist has never had a search produce a new concert
- **THEN** the artist's `last_found_at` MUST be null
