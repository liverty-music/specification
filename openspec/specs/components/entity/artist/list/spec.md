# Artist.List

## Purpose

Returns every registered artist.

## Requirements

### Requirement: List returns all registered artists
List SHALL return every registered artist, each with its fanart and fanart_sync_time. The order of the result is not defined.

#### Scenario: Registered artists exist
- **WHEN** three artists are registered
- **THEN** List returns those three artists

#### Scenario: No artists
- **WHEN** no artist is registered
- **THEN** List returns an empty list without error
