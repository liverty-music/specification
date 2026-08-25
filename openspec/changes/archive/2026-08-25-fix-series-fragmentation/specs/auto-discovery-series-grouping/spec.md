# auto-discovery-series-grouping Specification (delta)

## ADDED Requirements

### Requirement: Approval Preserves Series Grouping And Type

When a discovered series' `series_id` is resolved at discovery time, the system SHALL create its `series` row then (with its `title` and `SeriesType`), before any of its events — published or staged — reference it. A staged concert SHALL therefore carry only the `series_id` as a real foreign key. When an operator approves a staged concert, the system SHALL insert its event under that existing series and SHALL NOT mint a new SINGLE series per approved concert. Because the series row already exists, approval SHALL NOT materialize, adopt, or otherwise re-derive series identity.

#### Scenario: Approving a staged tour event joins the tour series
- **WHEN** a tour event was staged (unresolved venue or same-slot conflict) while its siblings auto-published into a TOUR series
- **THEN** approving the staged event SHALL insert it into that same `series_id`
- **AND** it SHALL NOT create a new series

#### Scenario: SeriesType is preserved through approval
- **WHEN** a staged event belongs to a discovered `<tour>` series
- **THEN** the approved event's series SHALL have `type = SERIES_TYPE_TOUR`
- **AND** the type SHALL NOT default to SINGLE

#### Scenario: All-staged series already has its series row
- **WHEN** every event of a discovered series was staged (none auto-published)
- **THEN** the series row SHALL already exist (created when its `series_id` was resolved at discovery)
- **AND** approving any staged event SHALL insert it under that existing `series_id` without creating a second series row

#### Scenario: A fully-rejected series leaves no orphaned data
- **WHEN** a discovered series had all its events staged and every one is later rejected
- **THEN** a cleanup SHALL remove the series row that has no events and no pending staged rows
