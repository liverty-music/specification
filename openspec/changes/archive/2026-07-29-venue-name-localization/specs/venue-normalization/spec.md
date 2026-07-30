## ADDED Requirements

### Requirement: Google Places API Request Includes Language Code

When the concert creation pipeline calls Google Places `SearchPlace`, the request SHALL include a `languageCode` field derived from the venue's country code. The country code SHALL be extracted from the ISO 3166-2 `admin_area` field (e.g., `"JP-13"` → `"JP"`). The mapping from country code to BCP 47 language tag SHALL follow a static lookup table with `"en"` as the default.

#### Scenario: Japanese venue resolves with Japanese language code

- **WHEN** the concert creation pipeline calls `SearchPlace` for a venue with `admin_area` starting with `"JP"`
- **THEN** the Places API request SHALL include `languageCode: "ja"`
- **AND** the returned canonical `venue.name` SHALL be in Japanese when available

#### Scenario: Korean venue resolves with Korean language code

- **WHEN** the concert creation pipeline calls `SearchPlace` for a venue with `admin_area` starting with `"KR"`
- **THEN** the Places API request SHALL include `languageCode: "ko"`

#### Scenario: Unknown country defaults to English language code

- **WHEN** the concert creation pipeline calls `SearchPlace` for a venue whose country code is not in the static mapping
- **THEN** the Places API request SHALL include `languageCode: "en"`

#### Scenario: Absent admin_area defaults to English language code

- **WHEN** the concert creation pipeline calls `SearchPlace` for a venue with no `admin_area`
- **THEN** the Places API request SHALL include `languageCode: "en"`

### Requirement: listed_venue_name Is Normalized Before Storage

The concert creation pipeline SHALL apply `NormalizeVenueName` to the scraped `listed_venue_name` before storing it in the `staged_concerts` row. The raw (unnormalized) value SHALL NOT be persisted.

#### Scenario: Prefecture prefix stripped before storage

- **WHEN** the concert creation pipeline processes a scraped concert with `listed_venue_name` equal to `"大阪・フェスティバルホール"`
- **THEN** the stored `listed_venue_name` SHALL be `"フェスティバルホール"`

#### Scenario: Whitespace-only listed_venue_name is rejected

- **WHEN** `NormalizeVenueName` reduces the scraped venue name to an empty string after normalization
- **THEN** the concert SHALL be treated the same as having a missing `listed_venue_name`

#### Scenario: Already-normalized name is stored unchanged

- **WHEN** the concert creation pipeline processes a scraped concert with `listed_venue_name` equal to `"日本武道館"`
- **THEN** the stored `listed_venue_name` SHALL be `"日本武道館"` (unchanged, normalization is idempotent)
