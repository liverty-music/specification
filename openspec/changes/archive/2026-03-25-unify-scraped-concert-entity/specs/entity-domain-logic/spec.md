## ADDED Requirements

### Requirement: ScrapedConcerts collection type

The entity package SHALL provide a `ScrapedConcerts` type defined as `type ScrapedConcerts []*ScrapedConcert`.

#### Scenario: Type alias is usable as slice

- **WHEN** a `[]*ScrapedConcert` value is cast to `ScrapedConcerts`
- **THEN** it is usable as `ScrapedConcerts` without data loss

---

### Requirement: ScrapedConcerts.FilterNew deduplication

The `ScrapedConcerts` type SHALL provide a `FilterNew(existing []*Concert) ScrapedConcerts` method that returns only the scraped concerts that do not conflict with existing concerts, applying date-only deduplication.

Deduplication rules:
1. Build a `seenDate` set from `existing` concerts using `LocalDate.Format("2006-01-02")`.
2. Iterate through the receiver slice in order. For each scraped concert:
   - Compute its date key as `LocalDate.Format("2006-01-02")`.
   - If the key is already in `seenDate`, skip it (duplicate).
   - Otherwise, add the key to `seenDate` and include it in the result.
3. Return the filtered slice. If no new concerts remain, return nil (not an empty slice).

This method handles both cross-batch deduplication (against existing DB concerts) and within-batch deduplication (multiple scraped concerts on the same date).

#### Scenario: Empty scraped list

- **WHEN** `ScrapedConcerts` is nil or empty and `existing` is any value
- **THEN** `FilterNew` returns nil

#### Scenario: No existing concerts

- **WHEN** `existing` is empty and `scraped` has concerts on different dates
- **THEN** `FilterNew` returns all scraped concerts

#### Scenario: All scraped concerts conflict with existing

- **WHEN** every scraped concert has a date matching an existing concert
- **THEN** `FilterNew` returns nil

#### Scenario: Partial overlap with existing

- **WHEN** scraped has 3 concerts, 1 conflicts with existing and 2 do not
- **THEN** `FilterNew` returns the 2 non-conflicting concerts in original order

#### Scenario: Within-batch duplicate on same date

- **WHEN** scraped contains 2 concerts on the same date (no existing concerts)
- **THEN** `FilterNew` returns only the first one (within-batch dedup)

#### Scenario: Within-batch duplicate conflicts with existing

- **WHEN** scraped contains 2 concerts on the same date, and that date also exists in `existing`
- **THEN** `FilterNew` returns nil (both are filtered)

#### Scenario: Preserves original order

- **WHEN** scraped has concerts on dates [Mar 15, Mar 17, Mar 16] and none conflict
- **THEN** `FilterNew` returns them in the same order [Mar 15, Mar 17, Mar 16]

#### Scenario: Nil existing concerts

- **WHEN** `existing` is nil and `scraped` has concerts
- **THEN** `FilterNew` returns all scraped concerts (no existing to conflict with)

---

### Requirement: ScrapedConcert JSON serialization

The `ScrapedConcert` struct SHALL have JSON tags on all fields to support serialization as an event payload.

Field-to-JSON-tag mapping:
- `Title` → `"title"`
- `ListedVenueName` → `"listed_venue_name"`
- `AdminArea` → `"admin_area,omitempty"`
- `LocalDate` → `"local_date"`
- `StartTime` → `"start_time,omitempty"`
- `OpenTime` → `"open_time,omitempty"`
- `SourceURL` → `"source_url"`

#### Scenario: Marshal omits nil optional fields

- **WHEN** a `ScrapedConcert` with `AdminArea=nil`, `StartTime=nil`, `OpenTime=nil` is marshaled to JSON
- **THEN** the JSON output does not contain `"admin_area"`, `"start_time"`, or `"open_time"` keys

#### Scenario: Marshal includes all non-nil fields

- **WHEN** a `ScrapedConcert` with all fields set is marshaled to JSON
- **THEN** all 7 fields appear in the JSON output with correct key names

## REMOVED Requirements

### Requirement: Scraped concert deduplication key

**Reason**: `DateKey()` was a thin wrapper around `LocalDate.Format("2006-01-02")` with no semantic content beyond the format string. Now that `FilterNew` owns the deduplication logic, there is no caller that needs to extract the key externally. The format string is inlined directly in `FilterNew`.

**Migration**: Remove `DateKey()` method from `ScrapedConcert`. Remove `TestScrapedConcert_DateKey` test.

---

### Requirement: ScrapedConcertData event DTO

**Reason**: Replaced by `ScrapedConcert` with JSON tags. The two types were structurally identical; the separation was an accidental artifact of the EDA introduction and provided no semantic distinction.

**Migration**: Replace all references to `entity.ScrapedConcertData` with `entity.ScrapedConcert`. The JSON field names are unchanged, so event consumers require no modification.
