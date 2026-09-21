# Venue

## Purpose

Defines the Venue entity, constructed from scraped source data, its normalized administrative area, and the uniqueness constraint that prevents duplicate venues for the same listed name and area.

## Requirements

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

### Requirement: Venue AdminArea Persistence

The system SHALL store the administrative area extracted by Gemini on the Venue record when available.

#### Scenario: AdminArea stored on new venue creation

- **WHEN** a new venue is created and the scraped concert includes a non-empty `admin_area`
- **THEN** the venue record SHALL have `admin_area` set to that value

#### Scenario: AdminArea is NULL when not extracted

- **WHEN** a new venue is created and the scraped concert has no `admin_area` (empty or absent)
- **THEN** the venue record SHALL have `admin_area` set to `NULL`

### Requirement: Venue constructor from scraped data

The entity package SHALL provide `NewVenueFromScraped(name string) *Venue` that creates a Venue with auto-generated UUIDv7 ID, Name=name, EnrichmentStatus=pending, and RawName=name.

#### Scenario: Constructor sets defaults

- **WHEN** NewVenueFromScraped("Zepp Tokyo") is called
- **THEN** returned Venue has non-empty ID, Name="Zepp Tokyo", RawName="Zepp Tokyo", EnrichmentStatus=EnrichmentStatusPending

---

### Requirement: Unique index on venue listed name and admin area

The `venues` table SHALL have a unique index on `(listed_venue_name, admin_area)` to prevent duplicate venue records for the same scraped name and area combination, and to support efficient lookup.

#### Scenario: Duplicate listed name and admin area rejected

- **WHEN** a venue is inserted with the same `listed_venue_name` and `admin_area` as an existing record
- **THEN** the database SHALL reject the insert via the unique constraint
- **AND** `VenueRepository.Create` SHALL handle the conflict gracefully (return the existing venue or ignore)

#### Scenario: Same listed name with different admin area allowed

- **WHEN** two venues share the same `listed_venue_name` but have different `admin_area` values (or one is NULL)
- **THEN** both records SHALL be permitted by the unique index
