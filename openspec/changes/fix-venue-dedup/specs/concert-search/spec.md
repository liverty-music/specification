## MODIFIED Requirements

### Requirement: Concert Deduplication Natural Key

The `executeSearch` dedup logic SHALL use the natural key `(local_event_date, start_at_utc)` to determine whether a scraped concert already exists in the database. The venue name is excluded from the dedup key because an artist cannot perform at two different venues simultaneously on the same day. The comparison SHALL normalize timezone differences and handle `start_at` nil states according to the rules defined below. The dedup SHALL apply both when comparing scraped concerts against existing DB records and when comparing scraped concerts within the same batch.

#### Scenario: Same instant expressed in different timezones

- **WHEN** a scraped concert has `start_at = 2026-06-01T18:00:00+09:00` (JST)
- **AND** an existing concert has `start_at = 2026-06-01T09:00:00Z` (UTC)
- **AND** both have the same `local_event_date`
- **THEN** the scraped concert SHALL be treated as a duplicate
- **AND** SHALL NOT be published in the `concert.discovered.v1` event

#### Scenario: Scraped concert has nil start_at, existing has start_at

- **WHEN** a scraped concert has `start_at = nil`
- **AND** an existing concert has a non-nil `start_at`
- **AND** both have the same `local_event_date`
- **THEN** the scraped concert SHALL be treated as a duplicate
- **AND** SHALL NOT be published
- **AND** the nil `start_at` SHALL NOT overwrite the existing value (the existing record already has richer information)

#### Scenario: Scraped concert has start_at, existing has nil

- **WHEN** a scraped concert has a non-nil `start_at`
- **AND** an existing concert has `start_at = nil`
- **AND** both have the same `local_event_date`
- **THEN** the scraped concert SHALL be published in the `concert.discovered.v1` event
- **AND** the downstream UPSERT SHALL update the existing record's `start_at` with the newly discovered value

#### Scenario: Both have non-nil start_at representing different instants

- **WHEN** a scraped concert has a non-nil `start_at`
- **AND** an existing concert has a non-nil `start_at`
- **AND** both have the same `local_event_date`
- **AND** the two `start_at` values represent different instants after UTC normalization (e.g., matinee 13:00 UTC vs evening 18:00 UTC)
- **THEN** the scraped concert SHALL be treated as a distinct event (separate show)
- **AND** SHALL be published in the `concert.discovered.v1` event

#### Scenario: Both have nil start_at, same date

- **WHEN** a scraped concert has `start_at = nil`
- **AND** an existing concert has `start_at = nil`
- **AND** both have the same `local_event_date`
- **THEN** the scraped concert SHALL be treated as a duplicate
- **AND** SHALL NOT be published

#### Scenario: Different date

- **WHEN** a scraped concert has a different `local_event_date` from an existing concert
- **THEN** the scraped concert SHALL be treated as a distinct event
- **AND** SHALL be published regardless of `start_at` values

#### Scenario: Within-batch dedup — same instant in different timezones

- **WHEN** two scraped concerts in the same Gemini response have the same `local_event_date`
- **AND** their `start_at` values represent the same instant after UTC normalization
- **THEN** only the first concert SHALL be included in the `concert.discovered.v1` event
- **AND** the second SHALL be discarded as a within-batch duplicate

#### Scenario: Within-batch — genuinely different start_at

- **WHEN** two scraped concerts in the same Gemini response have the same `local_event_date`
- **AND** their `start_at` values represent different instants after UTC normalization
- **THEN** both concerts SHALL be included in the `concert.discovered.v1` event (matinee/evening shows)

### Requirement: Dedup Key Comparison for Existing Concerts

The dedup logic SHALL build a lookup set from existing DB concerts using `ListByArtist(upcomingOnly=true)`. When `Event.ListedVenueName` is `nil` (legacy rows inserted before this field was added), the existing concert SHALL still participate in dedup using the `(local_event_date, start_at)` key.

#### Scenario: Existing concert with nil ListedVenueName still participates in dedup

- **WHEN** an existing concert has `ListedVenueName = nil` (legacy data)
- **THEN** it SHALL still be added to the dedup lookup set using `(local_event_date, start_at_utc)` as the key

#### Scenario: Existing concert with non-nil ListedVenueName is included

- **WHEN** an existing concert has a non-nil `ListedVenueName`
- **THEN** it SHALL be added to the dedup lookup set using `(local_event_date, start_at_utc)` as the key

## REMOVED Requirements

### Requirement: Resilience to Gemini API Non-Determinism — Scenario: Same date, different venue

**Reason**: The venue name is no longer part of the dedup key. The scenario "Same date, different venue → treated as distinct event" is no longer applicable because dedup is now based on `(date, start_at)` only. Two concerts on the same date with the same start_at are always considered duplicates regardless of venue name.

**Migration**: Events at the same date and start_at that were previously considered distinct due to different venue names will now be deduplicated. The data cleanup migration ensures a clean starting state.
