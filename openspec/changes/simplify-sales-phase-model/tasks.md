## 1. Specification & Proto (specification repo)

- [ ] 1.1 Remove `event_ids` and `anchor_event_id` from `liverty_music.entity.v1.SalesPhase`; update field documentation to describe a series-level phase
- [ ] 1.2 Run buf lint/format/breaking locally (breaking is expected and intended); confirm the only breaking deltas are the two removed fields
- [ ] 1.3 Open the specification PR with the proto change + this OpenSpec change; merge after review and CI pass
- [ ] 1.4 Publish a GitHub Release (tag `vX.Y.Z`) to trigger `buf-release.yml` → BSR push; monitor the workflow to success

## 2. Backend — entity & repository (prepared in parallel, finalized after BSR gen)

- [ ] 2.1 Remove covered-event fields from `entity.SalesPhase` and `entity.SalesPhaseCandidate` (`CoveredEventIDs`, `AnchorEventID`); drop `SalesSeriesCandidate.CandidateEvents` plumbing and `SalesPhaseCandidateEvent`
- [ ] 2.2 Change `SalesPhaseRepository.Upsert` to match on `(series_id, apply_start_at)`: found → update descriptive fields in place (return Updated), absent → insert new id (return Inserted); remove the covered-event overlap query and channel-compatibility rule
- [ ] 2.3 Remove `event_sales_phases` writes, `ReplaceCoveredEvents`, and covered-event hydration from the repository; keep upsert-only semantics (empty extraction never deletes)
- [ ] 2.4 Drop the "at least one covered event" persistence guard; persist on known `apply_start_time` alone

## 3. Backend — searcher

- [ ] 3.1 Remove Step-1 `covered_dates` from the extraction prompt/XML and the example template
- [ ] 3.2 Remove Step-2 `covered_event_indices` resolution and helpers (`resolveCoveredEvents`, `earliestEventID`, all-performances marker); stop passing candidate events into the search
- [ ] 3.3 Update searcher unit tests to assert series-level candidates with no covered-event resolution

## 4. Backend — audience (tracking-based)

- [ ] 4.1 Add `TicketJourneyRepository` reverse query: distinct user IDs with `status = Tracking` on any event of a given `series_id`
- [ ] 4.2 Replace `ResolveSalesPhaseAudience` (covered-event performers + proximity + follower + hype) with the tracking-journey lookup keyed by the phase's `series_id`
- [ ] 4.3 Update the announcement use case and the reminder scan to consume the new audience resolver; remove now-unused follower/hype wiring on this path

## 5. Backend — database migration

- [ ] 5.1 Author the migration: drop the `event_sales_phases` table and the `sales_phases.anchor_event_id` column
- [ ] 5.2 Verify existing `sales_phases` rows remain valid under the new convergence (they retain `series_id` + `apply_start_at`); hash/validate the migration in atlas format

## 6. Backend — package upgrade, swap, verification

- [ ] 6.1 After BSR gen completes, bump the generated schema package to `vX.Y.Z`; run `go mod tidy`
- [ ] 6.2 Swap call sites to the generated `SalesPhase` shape (no `event_ids`/`anchor_event_id`) at the TODO markers; resolve compile errors
- [ ] 6.3 Run `make check` (build, vet, unit tests) until green
- [ ] 6.4 Open the backend PR only after the package upgrade + swap pass locally; merge after review and CI pass

## 7. Ship to production

- [ ] 7.1 Publish the backend GitHub Release (tag `vX.Y.Z`) to retag the dev AR image to prod
- [ ] 7.2 Confirm ArgoCD syncs the new backend image and the sales-phase-discovery / sales-reminders CronJobs run on the updated code
- [ ] 7.3 Verify in prod directly: a discovery run upserts series-level phases (no covered-event rows), announcements/reminders reach tracking fans, and no duplicate announcements occur across re-runs
