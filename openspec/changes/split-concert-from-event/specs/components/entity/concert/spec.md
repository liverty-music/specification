## MODIFIED Requirements

### Requirement: A concert is exactly one event

A Concert SHALL extend exactly one Event and carry that Event's id; it adds only the performing Artists. A Concert SHALL have no title, type or source page of its own; they are read from the Series of the Event it extends.

#### Scenario: Title comes from the series
- **WHEN** a Concert extends an Event of a Series titled "ARENA TOUR 2026"
- **THEN** the Concert's title is "ARENA TOUR 2026"

#### Scenario: Concert id is its event id
- **WHEN** a Concert extends the Event with id E
- **THEN** the Concert's id is E
