<!-- spec: bubble-state-management | target: components/infrastructure/fan/web/route/discovery | flags: CLASSNAME | new_name: Bubble invariants are applied once at the field boundary -->

### Requirement: Bubble invariants are applied once at the field boundary
The invariants — exclude followed artists, deduplicate by name/id/mbid, and enforce the 50-bubble capacity — SHALL be applied exactly once, when the field owner produces or updates the field. Downstream consumers (router hooks, genre/reset/search flows, the physics layer) SHALL NOT re-apply these invariants independently.

#### Scenario: Followed exclusion happens once
- **WHEN** the field is produced or updated from any source (initial load, cache re-entry, genre, reset, similar top-up)
- **THEN** followed-artist exclusion SHALL be applied by the field owner as part of producing the field
- **AND** no consumer SHALL re-filter followed artists after the field is produced

#### Scenario: Capacity enforced once
- **WHEN** the field is produced or updated
- **THEN** the 50-bubble capacity SHALL be enforced by the field owner
- **AND** the physics layer SHALL receive a field already within capacity and SHALL NOT re-cap it
