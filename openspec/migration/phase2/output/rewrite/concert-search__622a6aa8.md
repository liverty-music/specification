<!-- spec: concert-search | target: components/usecase/concert/search-new-concerts | flags: CLASSNAME | new_name: Concert Deduplication Natural Key -->

### Requirement: Concert Deduplication Natural Key

The concert search's dedup logic SHALL use the natural key `(local_event_date, listed_venue_name, start_at_utc)` to determine whether a scraped concert already exists in the database. The comparison SHALL normalize timezone differences and handle `start_at` nil states according to the rules defined below. The dedup SHALL apply both when comparing scraped concerts against existing DB records and when comparing scraped concerts within the same batch.

#### Scenario: Same instant expressed in different timezones

- **WHEN** a scraped concert has `start_at = 2026-06-01T18:00:00+09:00` (JST)
- **AND** an existing concert has `start_at = 2026-06-01T09:00:00Z` (UTC)
- **AND** both have the same `local_event_date` and `listed_venue_name`
- **THEN** the scraped concert SHALL be treated as a duplicate
- **AND** SHALL NOT be published in the `concert.discovered.v1` event

#### Scenario: Scraped concert has nil start_at, existing has start_at

- **WHEN** a scraped concert has `start_at = nil`
- **AND** an existing concert has a non-nil `start_at`
- **AND** both have the same `local_event_date` and `listed_venue_name`
- **THEN** the scraped concert SHALL be treated as a duplicate
- **AND** SHALL NOT be published
- **AND** the nil `start_at` SHALL NOT overwrite the existing value (the existing record already has richer information)

#### Scenario: Scraped concert has start_at, existing has nil

- **WHEN** a scraped concert has a non-nil `start_at`
- **AND** an existing concert has `start_at = nil`
- **AND** both have the same `local_event_date` and `listed_venue_name`
- **THEN** the scraped concert SHALL be published in the `concert.discovered.v1` event
- **AND** the downstream UPSERT SHALL update the existing record's `start_at` with the newly discovered value

#### Scenario: Both have non-nil start_at representing different instants

- **WHEN** a scraped concert has a non-nil `start_at`
- **AND** an existing concert has a non-nil `start_at`
- **AND** both have the same `local_event_date` and `listed_venue_name`
- **AND** the two `start_at` values represent different instants after UTC normalization (e.g., matinee 13:00 UTC vs evening 18:00 UTC)
- **THEN** the scraped concert SHALL be treated as a distinct event (separate show)
- **AND** SHALL be published in the `concert.discovered.v1` event

#### Scenario: Both have nil start_at, same date and venue

- **WHEN** a scraped concert has `start_at = nil`
- **AND** an existing concert has `start_at = nil`
- **AND** both have the same `local_event_date` and `listed_venue_name`
- **THEN** the scraped concert SHALL be treated as a duplicate
- **AND** SHALL NOT be published

#### Scenario: Same date, different venue

- **WHEN** a scraped concert has the same `local_event_date` as an existing concert
- **AND** the `listed_venue_name` values differ
- **THEN** the scraped concert SHALL be treated as a distinct event
- **AND** SHALL be published regardless of `start_at` values

#### Scenario: Different date, same venue

- **WHEN** a scraped concert has a different `local_event_date` from an existing concert
- **AND** the `listed_venue_name` values match
- **THEN** the scraped concert SHALL be treated as a distinct event
- **AND** SHALL be published regardless of `start_at` values

#### Scenario: Within-batch dedup — same instant in different timezones

- **WHEN** two scraped concerts in the same Gemini response have the same `local_event_date` and `listed_venue_name`
- **AND** their `start_at` values represent the same instant after UTC normalization
- **THEN** only the first concert SHALL be included in the `concert.discovered.v1` event
- **AND** the second SHALL be discarded as a within-batch duplicate

#### Scenario: Within-batch — genuinely different start_at at same venue

- **WHEN** two scraped concerts in the same Gemini response have the same `local_event_date` and `listed_venue_name`
- **AND** their `start_at` values represent different instants after UTC normalization
- **THEN** both concerts SHALL be included in the `concert.discovered.v1` event (matinee/evening shows)
