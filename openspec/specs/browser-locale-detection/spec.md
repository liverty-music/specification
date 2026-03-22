# Browser Locale Detection

## Purpose

Provides a utility to detect the user's country from browser environment data without requiring geolocation permission or user interaction. Used to personalize Discovery page results based on the user's inferred location.

---

## Requirements

### Requirement: Timezone-based country detection
The system SHALL detect the user's country from the browser's IANA timezone identifier using `Intl.DateTimeFormat().resolvedOptions().timeZone`.

#### Scenario: Known timezone maps to a country
- **WHEN** the browser reports a recognized IANA timezone (e.g., `"Asia/Tokyo"`)
- **THEN** the system SHALL return the corresponding ISO 3166-1 country name (e.g., `"Japan"`)
- **AND** the mapping SHALL be performed synchronously without user interaction

#### Scenario: Unknown or generic timezone
- **WHEN** the browser reports `"UTC"`, `"Etc/GMT+9"`, or an unmapped timezone
- **THEN** the system SHALL return an empty string
- **AND** the caller SHALL treat empty string as "no country detected" (global fallback)

#### Scenario: API unavailable
- **WHEN** `Intl.DateTimeFormat` is not available in the browser environment
- **THEN** the system SHALL return an empty string without throwing an error

### Requirement: Mapping table coverage
The system SHALL maintain a static mapping table covering major IANA timezones for countries with meaningful Last.fm chart data.

#### Scenario: Mapping table entries
- **WHEN** the mapping table is consulted
- **THEN** it SHALL include at minimum the following timezone-to-country mappings:
  - `Asia/Tokyo` → `Japan`
  - `America/New_York`, `America/Chicago`, `America/Denver`, `America/Los_Angeles` → `United States`
  - `Europe/London` → `United Kingdom`
  - `Europe/Berlin`, `Europe/Paris`, `Europe/Rome`, `Europe/Madrid` → their respective countries
  - `Asia/Seoul` → `South Korea`
  - `Australia/Sydney`, `Australia/Melbourne` → `Australia`
  - `America/Toronto`, `America/Vancouver` → `Canada`
  - `America/Sao_Paulo` → `Brazil`
