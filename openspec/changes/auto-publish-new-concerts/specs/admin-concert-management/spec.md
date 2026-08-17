## ADDED Requirements

### Requirement: Admin console recently-auto-published review view

The admin console SHALL provide a review view that surfaces concerts that were
auto-published by the discovery pipeline, so an operator can retract a bad one after the
fact. The view SHALL present only auto-published concerts (origin = auto-published) within a
recency window (default 7 days from the auto-publish timestamp; configurable). Items SHALL
age out of the view automatically once they fall outside the window — no explicit
acknowledgement is required, so a correct auto-published concert costs the operator zero
clicks. Each row SHALL expose a delete action that invokes the admin `Delete` operation.

#### Scenario: View lists recently auto-published concerts

- **WHEN** an operator opens the recently-auto-published review view
- **THEN** it SHALL list concerts whose origin is auto-published and whose auto-publish
  timestamp is within the recency window
- **AND** it SHALL NOT list developer-approved concerts

#### Scenario: Items age out without acknowledgement

- **WHEN** an auto-published concert's auto-publish timestamp falls outside the recency window
- **THEN** it SHALL no longer appear in the review view
- **AND** no operator action SHALL have been required to clear it

#### Scenario: Operator deletes a bad auto-published concert

- **WHEN** an operator triggers delete on a row in the review view
- **THEN** the console SHALL call the admin `Delete` operation for that concert's event id

## MODIFIED Requirements

### Requirement: Admin lists every published concert

The admin `ConcertService` SHALL provide a `List` operation that returns every
published concert, with no follower, proximity, or personalization filtering, so an
operator can review the full published catalog. Each returned concert SHALL carry
the identifiers required for follow-up actions (the published event id, the
performing artist, and human-readable date/venue/title fields). Each returned concert
SHALL additionally carry its origin (auto-published vs developer-approved) and, when
auto-published, the auto-publish timestamp, so the console can present the
recently-auto-published review view. `List` SHALL NOT return concerts that are still
pending review (those are returned by `ListPending`).

#### Scenario: List returns all published concerts

- **WHEN** an admin calls `List`
- **THEN** every published concert SHALL be returned regardless of any follow or
  proximity relationship
- **AND** each entry SHALL include its published event id and performing artist

#### Scenario: List entries carry origin and auto-publish time

- **WHEN** an admin calls `List`
- **THEN** each returned concert SHALL indicate whether it was auto-published or
  developer-approved
- **AND** an auto-published concert SHALL carry its auto-publish timestamp

#### Scenario: Pending concerts are excluded from List

- **WHEN** concerts exist in both the published catalog and the pending review queue
- **THEN** `List` SHALL return only the published concerts
- **AND** the pending concerts SHALL be returned only by `ListPending`

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
