## ADDED Requirements

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

## REMOVED Requirements

### Requirement: Discovered concerts are staged, not published

**Reason**: The blanket "every discovered concert is staged for human approval" gate is
replaced. Now that search quality is sufficient, genuinely new concerts are auto-published on
discovery and only same-slot conflicts are staged. The staging queue no longer represents all
discovered concerts — only the conflict subset that needs human reconciliation.

**Migration**: Superseded by "Discovery auto-publishes new concerts and stages only conflicts".
The venue orphan-free guarantee is preserved by that requirement (a new `venues` row is created
only on the auto-publish path; a conflict resolves to the existing event's venue). No data
migration of existing `staged_concert` rows is required — remaining pending rows are still
resolved through the unchanged approval reconciliation.

### Requirement: Venue resolved at staging time, persisted at approval

**Reason**: Venue persistence timing changes. A `venues` row is now created on the auto-publish
path at discovery time (not at approval), and the conflict-staging path never creates a new
`venues` row because a same-slot conflict resolves to the already-published event's venue.

**Migration**: Superseded by "Discovery auto-publishes new concerts and stages only conflicts",
which owns the venue behavior: resolved-venue fields are denormalized onto the auto-published
event (publish path) or onto the `staged_concert` row for reviewer preview (conflict path), a
`venues` row is created only on the auto-publish path, and never-published concerts leave no
orphan `venues` rows.
