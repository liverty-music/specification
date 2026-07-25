## Why

Approving discovered concerts in the admin console fails with two hard errors —
`already_exists` (duplicate venue) and `failed_precondition` (equivalent event
already exists) — because dedup and identity are keyed on values that are not
stable across discovery runs. Google Places returns different `place_id`s for the
same physical venue (confirmed in prod: 和歌山ビッグホエール has two CIDs), and
Gemini returns the same venue under different `listed_venue_name` strings
(`フェスティバルホール` vs `大阪・フェスティバルホール`). The result: the approval
pipeline cannot recognise a venue/event it already created, so it crashes on the
unique constraint or dead-ends the reviewer. In one prod snapshot, at least 19
of 234 staged rows are stale re-discoveries that cannot be approved.

## What Changes

- **Venue resolution at approval becomes idempotent get-or-create.** Resolve by
  `google_place_id` first; on miss, fall back to `(listed_venue_name, admin_area)`;
  create only if neither matches, using `INSERT ... ON CONFLICT DO NOTHING` with a
  re-SELECT so a lost race or either unique index resolves to the existing row
  instead of erroring. The `admin_area` used for the fallback lookup and the insert
  MUST be derived the same way. `place_id` is authoritative; a found venue's NULL
  `place_id` MAY be backfilled, but an existing non-NULL `place_id` is never
  overwritten. Fixes the `already_exists` crash.
- **Discovery dedup keys on a stable venue identity, not the raw scraped string.**
  The pre-staging dedup against existing events and pending staged rows SHALL match
  on a normalized/canonical venue identity so that name-drift re-discoveries are
  recognised as already-known and are not re-staged. Reduces stale queue growth.
- **Approval reconciles a duplicate event instead of dead-ending.** When an
  approved staged concert maps to an event that already exists at the same
  `(venue_id, local_event_date, start_at)`, the reviewer is offered a choice
  between the existing record and the staged record rather than receiving
  `failed_precondition`. **BREAKING**: the admin `Approve` RPC gains a `resolution`
  input and a duplicate-conflict output (a proto/schema change).
- **Reconciliation is record-level.** Choosing "keep existing" logs the staged row
  to the rejection log with a duplicate reason and deletes it; choosing "adopt
  staged" overwrites the existing event's display fields
  (`listed_venue_name`, start/open time, title) while leaving `venue_id` and
  `place_id` untouched, then deletes the staged row.

## Capabilities

### New Capabilities
<!-- none — reuse existing capabilities -->

### Modified Capabilities
- `venue-normalization`: venue lookup/create becomes an idempotent get-or-create with
  `place_id`-authoritative identity, `(listed_venue_name, admin_area)` fallback,
  `ON CONFLICT DO NOTHING` + re-SELECT, unified `admin_area` derivation, and NULL-only
  `place_id` backfill.
- `concert-search`: the concert-dedup natural key SHALL match on a stable venue
  identity so venue-name drift across runs does not defeat dedup against existing
  events and pending staged rows.
- `concert-approval-queue`: approval SHALL resolve venues idempotently and SHALL
  reconcile a duplicate existing event via reviewer choice instead of failing;
  "keep existing" logs+deletes the staged row, "adopt staged" overwrites the
  existing event's display fields.
- `admin-concert-management`: the admin `ConcertService.Approve` RPC SHALL accept a
  `resolution` selector and SHALL return a duplicate-conflict result carrying the
  existing event's fields when an unresolved duplicate is detected.

## Impact

- **Schema (specification repo / BSR)**: `rpc/admin/v1` `ConcertService.Approve`
  request/response messages gain conflict + resolution fields. Requires a
  specification release → BSR codegen before backend/frontend can consume the
  generated types (Cross-Repo Release Coordination).
- **Backend (Go)**: `resolveOrCreateVenue` / `createVenueFromStaged` in
  `internal/usecase/concert_admin_uc.go`; `VenueRepository.Create`/lookups in
  `internal/infrastructure/database/rdb/venue_repo.go`; `SearchNewConcerts` dedup in
  `internal/usecase/concert_uc.go` + `internal/entity/concert.go` (`FilterNew`);
  the admin `Approve` handler + usecase. No DB migration required (constraints and
  indexes already exist).
- **Frontend (Aurelia/TypeScript)**: admin console approval action gains a
  duplicate-reconciliation dialog (record-level keep-existing / adopt-staged).
- **Data**: existing stale staged rows become approvable/clearable through the new
  reconciliation path.
