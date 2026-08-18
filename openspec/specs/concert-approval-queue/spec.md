# Concert Approval Queue

## Purpose

Concerts discovered by the search pipeline are staged for human review before
they become fan-visible. Discovery resolves the venue and writes a `pending`
staged concert instead of publishing directly; a developer approves (publishing
the concert and notifying followers) or rejects (dropping it and appending to an
analysis-only log). This gates AI-sourced data quality while keeping rejection
non-permanent and re-discovery idempotent.
## Requirements
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
  local date, start time, open time, raw `listed_venue_name`, resolved venue (name, admin_area,
  place id), source URL, and discovered-time timestamp

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
SHALL retain the full set of reviewable fields (local date, start time, open time, listed
venue name, resolved venue, source URL, discovered timestamp) and their per-row approve and
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
  start time, open time, listed venue name, resolved venue (or unresolved indicator),
  source URL, and discovered timestamp
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

#### Scenario: Conflict dialog shows open time for both staged and existing

- **WHEN** approval detects a duplicate and presents the conflict dialog
- **THEN** the dialog SHALL show the open time for both the staged and the existing event
- **AND** absent open time values SHALL be displayed as a dash placeholder

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

### Requirement: Discovery auto-publishes new concerts and stages only conflicts

The `CONCERT.discovered` consumer SHALL resolve the venue and evaluate the discovered
concert for a same-slot conflict against the published catalog BEFORE deciding how to
persist it. When the discovered concert is genuinely new — no existing published event at
the resolved `(venue_id, local_event_date, start_at)` (the known-start "fill" of an
existing unknown-start row counts as new, not a conflict) — the consumer SHALL publish it
directly: create or reuse the `venues` row, insert the published
`series`/`events`/`event_performers` rows (reusing the existing bulk-insert and natural-key
UPSERT behavior), and publish `CONCERT.created` so follower notifications fire immediately.
It SHALL NOT write a `pending` staged row for a new concert. When a same-slot conflict IS
detected, the consumer SHALL instead persist a `pending` `staged_concert` row (carrying the
scraped fields and the resolved-venue preview) and SHALL NOT insert any published row or
publish `CONCERT.created`; that staged row is resolved later through the existing approval
reconciliation.

A `venues` row SHALL be created only on the auto-publish path. The conflict-staging path
SHALL NOT create a new `venues` row, because a same-slot conflict necessarily resolves to
the venue of the already-published event; thus rejected or never-approved concerts SHALL
NOT create orphan `venues` rows.

Auto-publish requires a resolved venue. When the scraped venue name does NOT resolve against the
venue provider, the consumer SHALL stage the concert for review rather than auto-publishing it, and
SHALL NOT create a `venues` row — publishing a venue with no provider identity and no coordinates
would exclude the concert from proximity matching and publish an unreviewed venue. A resolved venue
is necessary but not sufficient for auto-publish: a resolved venue that collides with an existing
event is still staged as a conflict.

#### Scenario: New concert is auto-published without staging

- **WHEN** the `CONCERT.discovered` consumer processes a discovered concert whose resolved
  `(venue_id, local_event_date, start_at)` has no existing published event
- **THEN** it SHALL create or reuse the `venues` row and insert the published event (with its
  series and performers)
- **AND** it SHALL publish `CONCERT.created`
- **AND** it SHALL NOT write a `pending` staged row

#### Scenario: Conflicting concert is staged for reconciliation

- **WHEN** the `CONCERT.discovered` consumer processes a discovered concert that maps onto an
  existing published event at the resolved `(venue_id, local_event_date, start_at)`
- **THEN** it SHALL persist a `pending` `staged_concert` row carrying the scraped fields and
  resolved-venue preview
- **AND** it SHALL NOT insert any published row and SHALL NOT publish `CONCERT.created`

#### Scenario: Known-start fill is treated as new, not a conflict

- **WHEN** a discovered concert has a known start time and the only existing published event at
  that venue and date has an unknown (NULL) start time
- **THEN** the consumer SHALL treat it as the new/publish path (filling the existing row per the
  established fill behavior) rather than staging it as a conflict

#### Scenario: Unresolved venue is staged, not auto-published

- **WHEN** the `CONCERT.discovered` consumer processes a discovered concert whose scraped venue name
  cannot be resolved against the venue provider
- **THEN** it SHALL persist a `pending` `staged_concert` row for review
- **AND** it SHALL NOT auto-publish the concert and SHALL NOT create a `venues` row

#### Scenario: Pending concerts are not fan-visible

- **WHEN** a concert is in `pending` state in the approval queue
- **THEN** it SHALL NOT be returned by any consumer-facing read RPC (`List`, `ListByFollower`,
  `ListWithProximity`)

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

### Requirement: Re-discovery skips suppressed concerts

When the search pipeline filters newly discovered concerts, it SHALL exclude any concert
whose natural key matches a suppression entry, in addition to the existing exclusions for
published events and `pending` staged rows. A suppressed natural key SHALL NOT be
auto-published and SHALL NOT be re-staged as `pending`, so an operator's deletion of a bad
auto-published concert is not undone by the next discovery run.

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

