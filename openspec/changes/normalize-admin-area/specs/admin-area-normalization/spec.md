## ADDED Requirements

### Requirement: Admin Area Normalization Function

The system SHALL provide a normalization function that converts free-text administrative area strings into ISO 3166-2 subdivision codes.

#### Scenario: Japanese prefecture name to ISO code

- **WHEN** the normalization function receives a Japanese prefecture name (e.g., "東京都", "東京", "愛知県", "愛知")
- **THEN** it SHALL return the corresponding ISO 3166-2 code (e.g., `JP-13`, `JP-23`)

#### Scenario: English prefecture name to ISO code

- **WHEN** the normalization function receives an English name (e.g., "Tokyo", "tokyo", "Aichi")
- **THEN** it SHALL return the corresponding ISO 3166-2 code (e.g., `JP-13`, `JP-23`)

#### Scenario: Unrecognized input

- **WHEN** the normalization function receives text that does not match any known administrative area
- **THEN** it SHALL return nil (no value)
- **AND** the caller SHALL treat this as "admin area unknown"

#### Scenario: Empty or whitespace-only input

- **WHEN** the normalization function receives an empty string or whitespace-only string
- **THEN** it SHALL return nil

### Requirement: Normalization in Concert Discovery Pipeline

The concert discovery pipeline SHALL normalize Gemini's free-text `admin_area` output to an ISO 3166-2 code before persisting venue data.

#### Scenario: Gemini returns recognizable admin_area

- **WHEN** the Gemini concert searcher returns a scraped event with `admin_area = "愛知県"`
- **THEN** the pipeline SHALL normalize the value to `JP-23` before creating or updating the venue record

#### Scenario: Gemini returns unrecognizable admin_area

- **WHEN** the Gemini concert searcher returns a scraped event with an unrecognizable `admin_area`
- **THEN** the pipeline SHALL set `admin_area` to NULL on the venue record

#### Scenario: Gemini prompt unchanged

- **WHEN** the Gemini concert searcher constructs its prompt
- **THEN** the prompt text and response schema SHALL remain unchanged from the current implementation
- **AND** normalization SHALL occur after parsing the Gemini response, not within the LLM interaction

### Requirement: Existing Data Migration

The system SHALL migrate existing free-text `venues.admin_area` values to ISO 3166-2 codes.

#### Scenario: Known prefecture migrated

- **WHEN** the migration runs on a venue with `admin_area = '東京'`
- **THEN** the value SHALL be updated to `'JP-13'`

#### Scenario: Unknown value set to NULL

- **WHEN** the migration runs on a venue with an unrecognizable `admin_area` value
- **THEN** the value SHALL be set to NULL
