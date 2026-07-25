## MODIFIED Requirements

### Requirement: Approval publishes the concert

The system SHALL provide an approval operation that, given a `pending` staged concert,
resolves the venue idempotently (see the venue get-or-create requirement), inserts the
published `series`/`events`/`event_performers` rows (reusing the existing bulk-insert and
natural-key UPSERT behavior), removes the staged row, and publishes `CONCERT.created`.
When approval maps the staged concert onto an event that already exists at the resolved
`(venue_id, local_event_date, start_at)`, the operation SHALL NOT dead-end with
`failed_precondition`; instead it SHALL return a duplicate-conflict outcome for reviewer
reconciliation (see the duplicate-event reconciliation requirement).

#### Scenario: Approve publishes and notifies

- **WHEN** a developer approves a `pending` staged concert whose event does not yet exist
- **THEN** the system SHALL insert the published event (and its series and performers)
- **AND** SHALL delete the staged row
- **AND** SHALL publish `CONCERT.created` so downstream notification consumers run

#### Scenario: Approve is idempotent

- **WHEN** an approve operation targets a staged concert that no longer exists (already
  approved or rejected)
- **THEN** the operation SHALL succeed without error and SHALL NOT create a duplicate event

#### Scenario: Approve of an existing-event duplicate does not crash

- **WHEN** an approve operation maps a staged concert onto an event that already exists at
  the resolved `(venue_id, local_event_date, start_at)`
- **THEN** the operation SHALL NOT return `already_exists` or `failed_precondition`
- **AND** SHALL surface a duplicate-conflict outcome instead

## ADDED Requirements

### Requirement: Approval reconciles a duplicate existing event

The system SHALL, when approval detects that a staged concert corresponds to an
already-published event at the same resolved `(venue_id, local_event_date, start_at)` —
covering both the exact-start duplicate and the unknown-start staged versus known-start
existing case — present the reviewer a record-level choice between the existing event and
the staged record and apply exactly one of two outcomes. The reconciliation SHALL only affect the
event's venue display name and any missing start/open time; it SHALL NOT change `venue_id`,
`google_place_id`, or the series title, because both sides already resolve to the same venue
and the title is shared across every member event of the series. On a keep-existing choice the
system SHALL append the staged row to the `rejected_concerts_log` with a duplicate reason and
SHALL delete the staged row, leaving the existing event unchanged; the reviewer identity SHALL
be captured on the log entry. On an adopt-staged choice the system SHALL overwrite the existing
event's `listed_venue_name` from the staged record and SHALL fill `start_at`/`open_at` only
where the existing value is NULL (a known start/open time SHALL NEVER be overwritten with a
staged NULL); it SHALL leave `venue_id`, `google_place_id`, and the series title unchanged, and
SHALL delete the staged row. An approval that reaches this path without an explicit reviewer
choice SHALL make no mutation and SHALL report the conflict.

#### Scenario: Reviewer keeps the existing event

- **WHEN** a duplicate existing event is detected and the reviewer chooses to keep the
  existing record
- **THEN** the system SHALL append the staged row to the `rejected_concerts_log` with a
  duplicate reason and the reviewer identity
- **AND** SHALL delete the staged row
- **AND** SHALL leave the existing event unchanged

#### Scenario: Reviewer adopts the staged record

- **WHEN** a duplicate existing event is detected and the reviewer chooses to adopt the
  staged record
- **THEN** the system SHALL overwrite the existing event's `listed_venue_name` from the
  staged record
- **AND** SHALL fill `start_at`/`open_at` only where the existing value is NULL
- **AND** SHALL leave the event's `venue_id`, `google_place_id`, and series title unchanged
- **AND** SHALL delete the staged row

#### Scenario: Adopt never overwrites a known start time with a staged NULL

- **WHEN** the existing event has a known `start_at` and the staged record has a NULL
  `start_at`
- **AND** the reviewer chooses to adopt the staged record
- **THEN** the system SHALL keep the existing known `start_at`
- **AND** SHALL still update the `listed_venue_name` from the staged record

#### Scenario: Conflict without a choice makes no change

- **WHEN** approval detects a duplicate existing event but the caller supplied no
  reconciliation choice
- **THEN** the system SHALL NOT mutate the event or the staged row
- **AND** SHALL report the duplicate conflict with the existing event's fields for review
