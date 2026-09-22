# Delete

## Purpose

Lets an administrator permanently remove a published concert, suppressing it from being re-discovered and re-published by the automated search pipeline.

## Requirements

### Requirement: Admin hard-deletes a published concert

The admin `ConcertService` SHALL provide a `Delete` operation that permanently
removes a published concert identified by its event id. The deletion SHALL cascade
through the database's referential integrity to every row that references the
event (performers, tickets, ticket journeys, ticket emails, merkle tree nodes, and
the series' sales phases). The operation SHALL be unconditional: it SHALL NOT be
blocked by the presence of dependent rows such as minted tickets or fan ticket
journeys. This is an operator correction tool; the absence of a guard is
intentional for the pre-launch internal surface. On deletion the system SHALL record
a suppression entry for the deleted event's natural key (`venue_id`, local event date,
`start_at` — independent of performing artist), regardless of the concert's origin, so
that a later discovery run does not re-create it (see the re-discovery suppression
requirement in `concert-approval-queue`).

#### Scenario: Delete removes the concert and cascades

- **WHEN** an admin calls `Delete` with a published concert's event id
- **THEN** the event and its concert record SHALL be removed
- **AND** all rows referencing that event SHALL be removed by database cascade

#### Scenario: Delete records a suppression entry

- **WHEN** an admin calls `Delete` with a published concert's event id
- **THEN** the system SHALL record a suppression entry for that concert's natural key
- **AND** a later discovery run producing that natural key SHALL NOT re-create the concert

#### Scenario: Delete is unconditional

- **WHEN** an admin calls `Delete` on a concert that has dependent rows
  (e.g. ticket journeys or minted tickets)
- **THEN** the deletion SHALL proceed and remove those dependent rows
- **AND** the operation SHALL NOT be rejected on account of the dependents

#### Scenario: Delete is idempotent

- **WHEN** a `Delete` targets an event id that no longer exists
- **THEN** the operation SHALL succeed without error

#### Scenario: Malformed event id is rejected

- **WHEN** a `Delete` is called with a missing or malformed event id
- **THEN** it SHALL be rejected with `INVALID_ARGUMENT`
- **AND** no concert SHALL be deleted

### Requirement: Deleting a published concert suppresses re-discovery

Deleting a published concert (via the admin `Delete` operation) SHALL record a suppression
entry keyed by the deleted event's natural key (resolved venue, local event date, and start
time) — the same `(venue_id, local_event_date, start_at)` identity the event is stored under,
independent of performing artist, so the suppression granularity matches the event-level
deletion. Suppression applies regardless of the deleted concert's origin (auto-published or
developer-approved): a deleted concert SHALL NOT silently return via auto-publish. Suppression
is a distinct, persistent concept from the analysis-only `rejected_concerts_log`: it exists
specifically to stop a concert an operator judged wrong from being auto-published or re-staged
again by a later discovery run. Suppression SHALL be reversible only through a deliberate
un-suppress path, not by ordinary re-discovery.

#### Scenario: Delete records a suppression entry

- **WHEN** an operator deletes a published concert
- **THEN** the system SHALL record a suppression entry for that concert's natural key

#### Scenario: Suppression is separate from the rejection log

- **WHEN** a suppression entry is recorded
- **THEN** it SHALL NOT be written to or read from the `rejected_concerts_log`
- **AND** the `rejected_concerts_log` SHALL remain analysis-only and non-suppressing
