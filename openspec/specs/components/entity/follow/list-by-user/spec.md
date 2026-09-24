# Follow.ListByUser

## Purpose

Lists the artists one fan follows, each with the fan's hype level for it.

## Requirements

### Requirement: ListByUser returns every followed artist with its hype level

ListByUser SHALL return one entry per Follow of the fan, each carrying the artist's id, name, MBID and fan art together with the Follow's hype level. The entries SHALL be in no particular order. When the fan follows no artist, ListByUser SHALL return an empty list, not an error.

#### Scenario: Fan follows three artists

- **WHEN** the fan follows three artists at Watch, Home and Away
- **THEN** three entries are returned, each with its artist and its hype level

#### Scenario: Fan follows nobody

- **WHEN** the fan has no Follow
- **THEN** an empty list is returned
