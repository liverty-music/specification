## ADDED Requirements

### Requirement: Venue Name Display Respects User's Preferred Language

The concert mapper SHALL select the venue display name based on the user's current language setting. For Japanese users, `listed_venue_name` (scraped from the artist's official site, typically Japanese) SHALL be preferred over `venue.name` (Google Places canonical). For English users, `venue.name` SHALL be preferred. Either direction SHALL fall back to the other field when the preferred field is absent.

#### Scenario: Japanese user sees listed_venue_name when available

- **WHEN** the concert mapper resolves the venue display name
- **AND** the user's current language is `ja`
- **AND** the concert has a non-empty `listed_venue_name`
- **THEN** the mapper SHALL use `listed_venue_name` as the venue display name

#### Scenario: Japanese user falls back to venue.name when listed_venue_name is absent

- **WHEN** the concert mapper resolves the venue display name
- **AND** the user's current language is `ja`
- **AND** the concert has no `listed_venue_name` (null or empty)
- **THEN** the mapper SHALL use `venue.name` as the venue display name

#### Scenario: English user sees venue.name when available

- **WHEN** the concert mapper resolves the venue display name
- **AND** the user's current language is `en`
- **AND** the concert's embedded venue has a non-empty `name`
- **THEN** the mapper SHALL use `venue.name` as the venue display name

#### Scenario: English user falls back to listed_venue_name when venue.name is absent

- **WHEN** the concert mapper resolves the venue display name
- **AND** the user's current language is `en`
- **AND** the concert's embedded venue has no name
- **THEN** the mapper SHALL use `listed_venue_name` as the venue display name

#### Scenario: Language parameter is injected into the mapper

- **WHEN** the concert mapper function (or class) is invoked
- **THEN** it SHALL accept the current language as an explicit parameter
- **AND** it SHALL NOT read the language directly from a global store or singleton
