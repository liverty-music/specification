## MODIFIED Requirements

### Requirement: ListByUser returns every followed artist with its hype level

ListByUser SHALL return one entry per Follow of the fan, each carrying the artist's id, name, MBID and fan art together with the Follow's hype level and who set it. The entries SHALL be in no particular order. When the fan follows no artist, ListByUser SHALL return an empty list, not an error.

#### Scenario: Fan follows three artists

- **WHEN** the fan follows three artists at Watch set by the fan, Nearby set by default and Away set by inference
- **THEN** three entries are returned, each with its artist, its hype level and who set it

#### Scenario: Fan follows nobody

- **WHEN** the fan has no Follow
- **THEN** an empty list is returned
