<!-- merge_group: REDISCOVERY-FILTER | target: components/usecase/concert/search-new-concerts | members: 2 -->
<!-- renamed_scenarios: 0 -->

### Requirement: Re-discovery dedup consults published, pending, and suppression state

When the search pipeline filters newly discovered concerts, it SHALL exclude any concert whose natural key already exists in the published `events` table, as a `pending` row in the staging queue, or as a suppression entry. It SHALL NOT consult the `rejected_concerts_log` for this filtering. A suppressed natural key SHALL NOT be auto-published and SHALL NOT be re-staged as `pending`, so an operator's deletion of a bad auto-published concert is not undone by the next discovery run.

#### Scenario: Already published is skipped

- **WHEN** a discovered concert's natural key matches an existing published event
- **THEN** it SHALL NOT be staged

#### Scenario: Already pending is refreshed, not duplicated

- **WHEN** a discovered concert's natural key matches an existing `pending` staged row
- **THEN** the system SHALL update that staged row's payload with the latest discovered data
- **AND** SHALL NOT create a second `pending` row for the same natural key

#### Scenario: Previously rejected is not suppressed

- **WHEN** a discovered concert's natural key matches only a `rejected_concerts_log` entry (and is
  absent from `events` and `pending` staging)
- **THEN** the concert SHALL be staged as `pending`

#### Scenario: Suppressed concert is not re-created

- **WHEN** a discovered concert's natural key matches a suppression entry
- **THEN** the concert SHALL NOT be auto-published
- **AND** SHALL NOT be staged as `pending`

#### Scenario: Un-suppressed concert can be discovered again

- **WHEN** a suppression entry for a natural key has been removed through the deliberate
  un-suppress path
- **AND** a later discovery run produces that natural key
- **AND** that natural key is absent from `events` and `pending` staging
- **THEN** the concert SHALL be eligible for auto-publish or conflict staging as normal
