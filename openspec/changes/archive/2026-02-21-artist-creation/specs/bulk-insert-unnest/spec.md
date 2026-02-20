## Purpose

This capability introduces the PostgreSQL `unnest` pattern for bulk insert operations, replacing manual placeholder construction in repository implementations.

## ADDED Requirements

### Requirement: Bulk artist creation via unnest
The `ArtistRepository.Create` SHALL be extended to variadic (`Create(ctx, artists ...*Artist) ([]*Artist, error)`) and SHALL persist artists using PostgreSQL's `unnest` array function, consistent with the existing `ConcertRepository.Create` variadic pattern.

#### Scenario: Bulk insert multiple artists
- **WHEN** `Create` is called with a slice of artists
- **THEN** the system SHALL insert all artists in a single SQL statement using `unnest` arrays
- **AND** the SQL SHALL use `ON CONFLICT (mbid) DO NOTHING` for deduplication
- **AND** the method SHALL return all artists (both newly inserted and pre-existing) with valid database IDs

#### Scenario: Empty slice input
- **WHEN** `Create` is called with an empty slice
- **THEN** the method SHALL return an empty slice without executing any SQL

#### Scenario: No parameter limit
- **WHEN** `Create` is called with any number of artists
- **THEN** the system SHALL NOT be constrained by PostgreSQL's 65,535 parameter limit
- **AND** no manual batch splitting SHALL be required

### Requirement: Concert bulk insert via unnest
The `ConcertRepository.Create` SHALL be refactored to use PostgreSQL's `unnest` array function instead of manual placeholder construction.

#### Scenario: Bulk insert concerts with unnest
- **WHEN** `Create` is called with multiple concerts
- **THEN** the system SHALL insert events and concert associations using `unnest` arrays
- **AND** both INSERT statements SHALL use `ON CONFLICT DO NOTHING`
- **AND** no manual batch splitting by `maxConcertsPerBatch` SHALL be required

#### Scenario: Single concert creation unchanged
- **WHEN** `Create` is called with a single concert argument
- **THEN** it SHALL behave identically to the previous implementation
