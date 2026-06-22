# admin-concert-management Specification

## Purpose
TBD - created by archiving change admin-console-concert-management. Update Purpose after archive.
## Requirements
### Requirement: Admin concert operations are served by a single ConcertService

The admin-scoped concert operations SHALL be served by a single
`liverty_music.rpc.admin.v1.ConcertService` — listing published concerts, listing
the pending review queue, approving, rejecting, and deleting. This service is distinct from
the consumer `liverty_music.rpc.concert.v1.ConcertService`; the proto package is
the sole disambiguator and the `admin.v1` package conveys the admin audience, so
the service name SHALL NOT carry an audience or role qualifier. Method names SHALL
be bare verbs (`List`, `ListPending`, `Approve`, `Reject`, `Delete`) because the
service name already carries the `Concert` entity.

#### Scenario: Admin concert service identity

- **WHEN** the admin concert RPC surface is defined
- **THEN** it SHALL be the service `liverty_music.rpc.admin.v1.ConcertService`
- **AND** its methods SHALL be `List`, `ListPending`, `Approve`, `Reject`, and `Delete`

#### Scenario: No collision with the consumer concert service

- **WHEN** both the consumer and admin concert services exist
- **THEN** they SHALL be distinguished by proto package
  (`rpc.concert.v1` vs `rpc.admin.v1`)
- **AND** neither service's fully-qualified name SHALL depend on a role suffix

### Requirement: Admin lists every published concert

The admin `ConcertService` SHALL provide a `List` operation that returns every
published concert, with no follower, proximity, or personalization filtering, so an
operator can review the full published catalog. Each returned concert SHALL carry
the identifiers required for follow-up actions (the published event id, the
performing artist, and human-readable date/venue/title fields). `List` SHALL NOT
return concerts that are still pending review (those are returned by `ListPending`).

#### Scenario: List returns all published concerts

- **WHEN** an admin calls `List`
- **THEN** every published concert SHALL be returned regardless of any follow or
  proximity relationship
- **AND** each entry SHALL include its published event id and performing artist

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
intentional for the pre-launch internal surface.

#### Scenario: Delete removes the concert and cascades

- **WHEN** an admin calls `Delete` with a published concert's event id
- **THEN** the event and its concert record SHALL be removed
- **AND** all rows referencing that event SHALL be removed by database cascade

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

### Requirement: Admin console presents approved concerts grouped by artist and series

The admin console SHALL present the published concerts returned by `List` grouped
first by performing artist and then by series, computed client-side from the flat
`List` result. Each series SHALL be a collapsed disclosure that expands to its
individual events; the collapsed view SHALL summarise the series (event count and
date range) so the catalog stays scannable without expanding every series. Each
expanded event SHALL show its local date, start time, open time, and venue, with a
per-event manual delete control. Event columns SHALL align across all series and
artists. Triggering delete SHALL open a modal confirmation; the `Delete` RPC SHALL
be issued only after the operator confirms.

#### Scenario: Concerts shown grouped by artist then series

- **WHEN** an operator opens the approved-concerts screen
- **THEN** the published concerts SHALL be displayed grouped by performing artist
- **AND** within each artist they SHALL be grouped into collapsible series
- **AND** each collapsed series SHALL show its event count and date range

#### Scenario: Expanding a series reveals its events

- **WHEN** an operator expands a series
- **THEN** its individual events SHALL be listed with local date, start time, open
  time, and venue
- **AND** each event SHALL expose a manual delete control

#### Scenario: Delete requires confirmation in a modal dialog

- **WHEN** an operator activates an event's delete control
- **THEN** a modal confirmation dialog SHALL open identifying the target concert
- **AND** the dialog's confirm control SHALL receive initial focus so it can be
  confirmed with the Enter key, and dismissed (without deleting) with Escape
- **AND** the `Delete` RPC SHALL be issued only after the operator confirms

