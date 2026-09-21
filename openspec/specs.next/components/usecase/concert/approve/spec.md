# Approve

## Purpose

Lets an operator approve a discovered concert for publication, resolving conflicts with existing duplicate events, preserving series grouping, and idempotently persisting the concert and its venue.

## Requirements

### Requirement: Approve resolves duplicate-event conflicts via a resolution selector

The admin `liverty_music.rpc.admin.v1.ConcertService.Approve` RPC SHALL accept an optional
`resolution` selector with the values `RESOLUTION_UNSPECIFIED`, `KEEP_EXISTING`, and
`ADOPT_STAGED`. When invoked with `RESOLUTION_UNSPECIFIED` (or the field unset) and the
staged concert maps onto an already-published event at the resolved
`(venue_id, local_event_date, start_at)`, the response SHALL carry a duplicate-conflict
result describing the existing event (its display fields) alongside the staged preview, and
the call SHALL NOT mutate state. When invoked with `KEEP_EXISTING` or `ADOPT_STAGED`, the
RPC SHALL apply the corresponding reconciliation outcome and complete the approval. A
non-duplicate approval SHALL behave exactly as before regardless of the `resolution` value.
The RPC SHALL remain idempotent and SHALL stay a single verb (`Approve`); no separate
conflict-resolution RPC is introduced. The RPC SHALL capture the calling reviewer's identity
so that a `KEEP_EXISTING` outcome can record it on the `rejected_concerts_log` entry.

#### Scenario: First approve of a duplicate returns a conflict

- **WHEN** an admin invokes `Approve` for a staged concert with `resolution` unset
- **AND** the staged concert maps onto an already-existing event
- **THEN** the response SHALL contain a duplicate-conflict result with the existing event's
  display fields and the staged preview
- **AND** the call SHALL NOT mutate the event or the staged row

#### Scenario: Approve with KEEP_EXISTING resolves the conflict

- **WHEN** an admin invokes `Approve` for the same staged concert with
  `resolution = KEEP_EXISTING`
- **THEN** the system SHALL apply the keep-existing reconciliation outcome
- **AND** the response SHALL indicate the staged row was cleared without changing the event

#### Scenario: Approve with ADOPT_STAGED resolves the conflict

- **WHEN** an admin invokes `Approve` for the same staged concert with
  `resolution = ADOPT_STAGED`
- **THEN** the system SHALL apply the adopt-staged reconciliation outcome
- **AND** the response SHALL indicate the existing event's `listed_venue_name` was updated
  (and any NULL start/open time filled), leaving `venue_id`, `google_place_id`, and series
  title unchanged

#### Scenario: Non-duplicate approve is unaffected by the selector

- **WHEN** an admin invokes `Approve` for a staged concert whose event does not yet exist
- **THEN** the concert SHALL be published normally
- **AND** the `resolution` value SHALL have no effect on the outcome

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

### Requirement: Concert Approval and Duplicate Reconciliation

The system SHALL provide an approval operation that, given a `pending` staged
concert, resolves the venue idempotently, inserts the published
`series`/`events`/`event_performers` rows (reusing the existing bulk-insert
and natural-key UPSERT behavior), removes the staged row, and publishes
`CONCERT.created`. The approve operation SHALL be idempotent: applying it to a
staged concert that no longer exists (already approved or rejected) SHALL
succeed without error and SHALL NOT create a duplicate event. When approval
maps the staged concert onto an event that already exists at the resolved
`(venue_id, local_event_date, start_at)`, the operation SHALL NOT dead-end
with `already_exists` or `failed_precondition`; instead the system SHALL
present the reviewer a record-level choice between the existing event and the
staged record and apply exactly one of two outcomes. The reconciliation SHALL
only affect the event's venue display name and any missing start/open time; it
SHALL NOT change `venue_id`, `google_place_id`, or the series title, because
both sides already resolve to the same venue and the title is shared across
every member event of the series. On a keep-existing choice the system SHALL
append the staged row to the `rejected_concerts_log` with a duplicate reason
and the reviewer identity, and SHALL delete the staged row, leaving the
existing event unchanged. On an adopt-staged choice the system SHALL overwrite
the existing event's `listed_venue_name` from the staged record and SHALL
fill `start_at`/`open_at` only where the existing value is NULL (a known
start/open time SHALL NEVER be overwritten with a staged NULL); it SHALL leave
`venue_id`, `google_place_id`, and the series title unchanged, and SHALL
delete the staged row. An approval that reaches this path without an explicit
reviewer choice SHALL make no mutation and SHALL report the conflict.

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

### Requirement: Concert Persistence

The system SHALL route any new concert discovered via the search mechanism into the approval queue
rather than persisting it directly. A discovered concert SHALL be staged in `pending` state and
SHALL be inserted into the published `events`/`concerts`/`series`/`event_performers` tables only
when a developer approves it. The `ConcertRepository.Create` method SHALL remain the persistence
path used at approval time: it SHALL accept a variadic number of concerts for bulk insert support
and SHALL use the PostgreSQL `unnest` pattern instead of manual placeholder construction.

#### Scenario: Discovered concerts are staged, not persisted

- **WHEN** `SearchNewConcerts` finds concerts not currently in the database
- **THEN** those concerts SHALL be staged in the approval queue in `pending` state
- **AND** they SHALL NOT be inserted into the `events`/`concerts` tables until approved

#### Scenario: Persist on approval

- **WHEN** a developer approves a pending staged concert
- **THEN** the concert SHALL be saved to the persisted storage via a single bulk insert call
- **AND** persisted with a valid ID

#### Scenario: Persist Venues on approval

- **WHEN** a staged concert is approved and its resolved venue does not exist in the database
- **THEN** a new venue is created based on the resolved venue from staging
- **AND** if an `admin_area` was extracted for the concert, it SHALL be stored on the venue record
- **AND** the new venue SHALL have `enrichment_status` set to `'pending'`
- **AND** the approved concert is associated with this new venue

#### Scenario: Bulk insert uses unnest

- **WHEN** `Create` is called with multiple concerts
- **THEN** the repository SHALL use `unnest` arrays for both `events` and `concerts` table inserts
- **AND** the implementation SHALL NOT use manual `fmt.Sprintf` placeholder construction
- **AND** no `maxConcertsPerBatch` batching loop SHALL be required

#### Scenario: Single concert creation

- **WHEN** `Create` is called with a single concert argument
- **THEN** it SHALL behave identically to the previous single-insert implementation

### Requirement: Concert UPSERT on Natural Key

The `ConcertRepository.Create` bulk insert SHALL use `ON CONFLICT` on the natural key to perform an UPSERT. When a conflict is detected, the existing record's `open_at` SHALL be updated if the new value provides previously unknown information. Since `start_at` is part of the natural key, a conflict implies both rows have the same `start_at` value (including both NULL); therefore `start_at` updates happen via new row insertion, not UPSERT update.

#### Scenario: Insert new event (no conflict)

- **WHEN** `Create` is called with a concert whose natural key does not exist
- **THEN** the event SHALL be inserted normally

#### Scenario: Different start_at inserts new row (not UPSERT)

- **WHEN** `Create` is called with a concert at the same `(venue_id, local_event_date)` as an existing event
- **AND** the `start_at` values differ (e.g., existing is NULL, new is non-NULL; or both are non-NULL but different instants)
- **THEN** the natural keys are distinct and no conflict occurs
- **AND** the new concert SHALL be inserted as a separate event row

#### Scenario: Conflict with richer open_at — update existing

- **WHEN** `Create` is called with a concert whose natural key matches an existing event
- **AND** the existing event has `open_at = NULL`
- **AND** the new concert has a non-NULL `open_at`
- **THEN** the existing event's `open_at` SHALL be updated to the new value via `COALESCE(EXCLUDED.open_at, events.open_at)`

#### Scenario: Conflict does not overwrite existing non-NULL open_at with NULL

- **WHEN** `Create` is called with a concert whose natural key matches an existing event
- **AND** the existing event already has a non-NULL `open_at`
- **AND** the new concert has `open_at = NULL`
- **THEN** the existing event's `open_at` SHALL NOT be overwritten
- **AND** SHALL retain its current value via `COALESCE(NULL, events.open_at)`

#### Scenario: Concerts row skipped for UPSERTed events with different UUID

- **WHEN** `Create` is called with a concert whose event UUID differs from the existing event at the same natural key
- **THEN** the events UPSERT SHALL update the existing row (keeping the original UUID)
- **AND** the input UUID SHALL NOT exist in the `events` table
- **AND** the `concerts` INSERT SHALL skip this row via `WHERE EXISTS` (no duplicate concerts row created)

### Requirement: Idempotent venue get-or-create with place_id-authoritative identity

The venue lookup-or-create path SHALL be idempotent and SHALL NOT fail when a venue
matching the resolved identity already exists. This path runs only when a staged concert is
approved (the sole caller that creates a `venues` row), and it supersedes the insert-only
create step described by the "Venue Resolution During Concert Creation" requirement. Identity
SHALL be resolved in this order:
(1) by `google_place_id` when the staged/scraped concert carries one; (2) on miss, by
`(listed_venue_name, admin_area)`; (3) only when neither matches SHALL a new `venues`
row be created. Creation SHALL use `INSERT … ON CONFLICT DO NOTHING` (untargeted, so a
violation on either the `google_place_id` partial-unique index or the
`(listed_venue_name, admin_area)` partial-unique index is absorbed) followed by a
re-SELECT on the same keys, so a lost race or a divergent identity resolves to the
existing row rather than surfacing an `already_exists` error.

The `admin_area` used for the `(listed_venue_name, admin_area)` fallback lookup and the
`admin_area` written on insert SHALL be derived identically (the resolved admin_area when
present, otherwise the raw scraped admin_area), so the read key and the write key never
diverge.

When the fallback lookup finds a venue whose `google_place_id` is NULL and the incoming
concert carries a resolved `google_place_id`, the system MAY backfill that value; it
SHALL NEVER overwrite an existing non-NULL `google_place_id`.

#### Scenario: No existing venue — a new row is created

- **WHEN** neither `google_place_id` nor `(listed_venue_name, admin_area)` matches an
  existing venue
- **THEN** the system SHALL insert a new `venues` row for the resolved identity
- **AND** SHALL return the newly created venue id

#### Scenario: Existing venue found by place_id

- **WHEN** a venue with the resolved `google_place_id` already exists
- **THEN** the system SHALL return that venue
- **AND** SHALL NOT attempt an insert

#### Scenario: place_id miss falls back to listed name and admin_area

- **WHEN** the resolved `google_place_id` does not match any existing venue
- **AND** a venue with the same `(listed_venue_name, admin_area)` already exists (with a
  different or NULL `google_place_id`)
- **THEN** the system SHALL return that existing venue
- **AND** SHALL NOT attempt to insert a new venue row
- **AND** SHALL NOT raise `already_exists`

#### Scenario: Concurrent create resolves to a single row

- **WHEN** two approvals resolve the same venue identity concurrently and both reach the
  insert step
- **THEN** the `ON CONFLICT DO NOTHING` insert SHALL suppress the losing insert
- **AND** the losing path SHALL re-SELECT by `google_place_id` then by
  `(listed_venue_name, admin_area)` and return the surviving row

#### Scenario: Fallback lookup and insert use the same admin_area

- **WHEN** a concert has a raw `admin_area` and no resolved `admin_area`
- **THEN** the fallback lookup and any subsequent insert SHALL both use the raw
  `admin_area`
- **AND** the lookup SHALL therefore match a row the insert would have collided with

#### Scenario: NULL place_id backfilled, non-NULL never overwritten

- **WHEN** the fallback finds an existing venue whose `google_place_id` is NULL
- **AND** the incoming concert carries a resolved `google_place_id`
- **THEN** the system MAY set the existing row's `google_place_id` to the resolved value
- **WHEN** the existing venue already has a non-NULL `google_place_id`
- **THEN** the system SHALL leave it unchanged
