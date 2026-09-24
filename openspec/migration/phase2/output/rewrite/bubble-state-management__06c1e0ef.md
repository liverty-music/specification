<!-- spec: bubble-state-management | target: components/infrastructure/fan/web/route/discovery | flags: CLASSNAME | new_name: Initial load tops up a sparse discovery field -->

### Requirement: Initial load tops up a sparse discovery field
When the user already follows artists, the initial load seeds bubbles from those artists' similar artists. Because the similar lists shrink as follow count grows (seeds are capped, the per-seed limit shrinks, and deduplication removes followed and overlapping artists), the system SHALL top up the field with global top artists whenever the deduplicated seed-similar results fall below 30 bubbles. Similar artists SHALL keep priority. This guarantees the field is never empty and stays reasonably full regardless of how many artists the user follows.

#### Scenario: Sparse seed-similar results are topped up
- **WHEN** the initial load takes the similar-seed path and the deduplicated similar results are below 30 bubbles
- **THEN** the system SHALL append global top artists (deduplicated against followed and already-included artists) up to the bubble cap
- **AND** the similar artists SHALL retain priority order ahead of the top-artist fillers

#### Scenario: Empty seed-similar still fills the field
- **WHEN** the similar lookups resolve to nothing (no matches, errors, or all results deduped away)
- **THEN** the system SHALL fill the field with global top artists rather than leaving it empty

#### Scenario: Sufficient seed-similar results are not diluted
- **WHEN** the deduplicated similar results meet or exceed 30 bubbles
- **THEN** the system SHALL NOT fetch or append top artists
