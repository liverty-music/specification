## ADDED Requirements

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
