# Artist.Get

## Purpose

Returns one registered artist by its id.

## Requirements

### Requirement: Get returns the artist with the id
Get SHALL return the artist with the given id, including its fanart and fanart_sync_time, and SHALL fail with NotFound when no artist has that id.

#### Scenario: Known id
- **WHEN** Get is called with the id of a registered artist
- **THEN** it returns that artist

#### Scenario: Unknown id
- **WHEN** Get is called with an id no artist has
- **THEN** Get fails with NotFound

#### Scenario: Malformed id
- **WHEN** Get is called with an id that is not a UUID
- **THEN** Get fails with InvalidArgument
