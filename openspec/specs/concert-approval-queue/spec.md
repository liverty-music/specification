# Concert Approval Queue

## Purpose

Concerts discovered by the search pipeline are staged for human review before
they become fan-visible. Discovery resolves the venue and writes a `pending`
staged concert instead of publishing directly; a developer approves (publishing
the concert and notifying followers) or rejects (dropping it and appending to an
analysis-only log). This gates AI-sourced data quality while keeping rejection
non-permanent and re-discovery idempotent.
## Requirements
### Requirement: Discovered concerts are staged, not published

A concert discovered by the search pipeline SHALL be written to a staging queue in a `pending`
state and SHALL NOT be inserted into the published `events`/`series`/`event_performers` tables
until a developer approves it. The `CONCERT.discovered` consumer SHALL perform venue resolution
up front and persist a `staged_concert` row; it SHALL NOT publish `CONCERT.created`.

#### Scenario: Discovery writes a pending staged concert

- **WHEN** the `CONCERT.discovered` consumer processes a newly discovered concert
- **THEN** it SHALL resolve the venue via Google Places
- **AND** it SHALL persist a `staged_concert` row in `pending` state carrying the scraped fields
  and the resolved-venue preview
- **AND** it SHALL NOT insert any row into `events`, `series`, or `event_performers`
- **AND** it SHALL NOT publish `CONCERT.created`

#### Scenario: Pending concerts are not fan-visible

- **WHEN** a concert is in `pending` state in the approval queue
- **THEN** it SHALL NOT be returned by any consumer-facing read RPC (`List`, `ListByFollower`,
  `ListWithProximity`)

### Requirement: Venue resolved at staging time, persisted at approval

The system SHALL resolve the venue (Google Places) when a concert is staged and SHALL denormalize
the resolved venue fields (place id, canonical name, admin_area, coordinates) onto the
`staged_concert` row for reviewer display. A `venues` row SHALL be created or looked up only when
the staged concert is approved, so that rejected or never-approved concerts SHALL NOT create
orphan `venues` rows.

#### Scenario: Resolved venue stored on the staged row

- **WHEN** a concert is staged and its venue resolves via Google Places
- **THEN** the resolved canonical venue name, `admin_area`, place id, and coordinates SHALL be
  stored on the `staged_concert` row
- **AND** no `venues` row SHALL be created at this point

#### Scenario: Venue row created on approval

- **WHEN** a staged concert is approved
- **THEN** the system SHALL create or reuse the `venues` row for the resolved venue
- **AND** associate the published event with it

#### Scenario: Rejected concert leaves no orphan venue

- **WHEN** a staged concert is rejected
- **THEN** no `venues` row SHALL have been created on its behalf

### Requirement: Approval publishes the concert

The system SHALL provide an approval operation that, given a `pending` staged concert, inserts the
published `series`/`events`/`event_performers` rows (reusing the existing bulk-insert and
natural-key UPSERT behavior), removes the staged row, and publishes `CONCERT.created`.

#### Scenario: Approve publishes and notifies

- **WHEN** a developer approves a `pending` staged concert
- **THEN** the system SHALL insert the published event (and its series and performers)
- **AND** SHALL delete the staged row
- **AND** SHALL publish `CONCERT.created` so downstream notification consumers run

#### Scenario: Approve is idempotent

- **WHEN** an approve operation targets a staged concert that no longer exists (already approved
  or rejected)
- **THEN** the operation SHALL succeed without error and SHALL NOT create a duplicate event

### Requirement: Rejection drops the concert and is non-permanent

The system SHALL provide a reject operation that removes a `pending` staged concert and records
the rejection in an append-only log. Rejection SHALL NOT permanently suppress the concert: a
later discovery run that produces the same natural key SHALL re-stage it as `pending` for
re-review.

#### Scenario: Reject drops and logs

- **WHEN** a developer rejects a `pending` staged concert with a reason
- **THEN** the system SHALL delete the staged row
- **AND** SHALL append a `rejected_concerts_log` entry capturing the raw scraped payload, the
  resolved-venue preview, the reason, the reviewer identity, and the timestamp

#### Scenario: Rejected concert can re-enter the queue

- **WHEN** a concert was previously rejected
- **AND** a later discovery run produces the same natural key
- **AND** that natural key is not present in `events` or as a `pending` staged row
- **THEN** the system SHALL re-stage it as `pending`

#### Scenario: Reject is idempotent

- **WHEN** a reject operation targets a staged concert that no longer exists
- **THEN** the operation SHALL succeed without error

### Requirement: Re-discovery dedup consults published and pending state

When the search pipeline filters newly discovered concerts, it SHALL exclude any concert whose
natural key already exists in the published `events` table OR as a `pending` row in the staging
queue. It SHALL NOT consult the `rejected_concerts_log` for this filtering.

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

### Requirement: Rejection log is append-only and analysis-only

The system SHALL maintain a `rejected_concerts_log` that is append-only and used solely for
searcher-quality analysis. It SHALL NOT participate in discovery dedup or otherwise suppress
future staging.

#### Scenario: Log does not affect staging

- **WHEN** the discovery pipeline evaluates whether to stage a concert
- **THEN** the presence of a matching `rejected_concerts_log` entry SHALL have no effect on the
  staging decision

### Requirement: Admin-scoped moderation RPCs

The system SHALL expose a `ConcertModerationService` whose RPCs are authorized only for the admin
org, consistent with the admin console authentication boundary. The service SHALL provide
operations to list pending concerts, approve a pending concert, and reject a pending concert with
a reason.

#### Scenario: Admin lists pending concerts

- **WHEN** an authenticated admin-org caller invokes `ListPendingConcerts`
- **THEN** the response SHALL contain each pending concert's staged id, performing artist, title,
  local date, start time, raw `listed_venue_name`, resolved venue (name, admin_area, place id),
  source URL, and discovered-time timestamp

#### Scenario: Non-admin caller is denied

- **WHEN** a caller outside the admin org invokes any `ConcertModerationService` RPC
- **THEN** the call SHALL be rejected with a permission error and SHALL NOT mutate state

#### Scenario: Approve and reject act on the identified staged concert

- **WHEN** an admin invokes `ApproveConcert` or `RejectConcert` with a staged concert id
- **THEN** the system SHALL apply the corresponding approval or rejection behavior to that staged
  concert

### Requirement: Admin console approval-queue UI

The admin console SHALL provide a reviewer screen that lists pending concerts grouped
first by performing artist and then by series title, and offers per-concert approve and
reject (with reason) actions. The screen SHALL live in the bundle-isolated `admin/` app
and SHALL consume the admin `ConcertService`. Grouping SHALL be computed client-side
from the flat `ListPending` result using the `PendingConcert.performer.name` and
`PendingConcert.title` fields as grouping keys (artist and series proxy respectively).

Each series group SHALL be presented as a collapsible disclosure. The collapsed summary
SHALL show the series title, the count of pending concerts in the group, and the count
of concerts with an unresolved venue. Individual concert rows within an expanded group
SHALL retain the full set of reviewable fields (local date, start time, listed venue
name, resolved venue, source URL, discovered timestamp) and their per-row approve and
reject controls. The Artist and Title columns SHALL NOT be repeated inside the group
table; they are conveyed by the group headers.

#### Scenario: Reviewer sees pending concerts grouped by artist and series

- **WHEN** an authenticated developer opens the approval-queue screen
- **THEN** the pending concerts SHALL be displayed grouped first by performing artist
- **AND** within each artist they SHALL be grouped into collapsible series using the
  concert title as the series proxy
- **AND** each collapsed series summary SHALL show the series title, the number of
  pending concerts in the group, and the number with an unresolved venue

#### Scenario: Expanding a series reveals per-concert review rows

- **WHEN** the developer expands a series group
- **THEN** each pending concert in that series SHALL be listed showing local date,
  start time, listed venue name, resolved venue (or unresolved indicator), source
  URL, and discovered timestamp
- **AND** each row SHALL expose Approve and Reject controls

#### Scenario: Reviewer approves an item

- **WHEN** the developer approves a pending concert
- **THEN** the UI SHALL call `Approve` and remove the row from its series group on success
- **AND** if the series group becomes empty it SHALL be removed from the UI

#### Scenario: Reviewer rejects an item with a reason

- **WHEN** the developer rejects a pending concert and provides a reason
- **THEN** the UI SHALL call `Reject` with that reason and remove the row from its
  series group on success
- **AND** if the series group becomes empty it SHALL be removed from the UI

