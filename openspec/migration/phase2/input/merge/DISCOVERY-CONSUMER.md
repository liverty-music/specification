<!-- merge_group: DISCOVERY-CONSUMER | target: components/usecase/concert/create-from-discovered | members: 2 -->

<!-- member: concert-approval-queue | flags:  -->
### Requirement: Rejection log is append-only and analysis-only

The system SHALL maintain a `rejected_concerts_log` that is append-only and used solely for
searcher-quality analysis. It SHALL NOT participate in discovery dedup or otherwise suppress
future staging.

#### Scenario: Log does not affect staging

- **WHEN** the discovery pipeline evaluates whether to stage a concert
- **THEN** the presence of a matching `rejected_concerts_log` entry SHALL have no effect on the
  staging decision

<!-- member: concert-approval-queue | flags:  -->
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

