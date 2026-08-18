## 1. Backend — data model

- [x] 1.1 Atlas migration: create `suppressed_concerts` keyed by the event triple `(venue_id, local_event_date, start_at)` with `NULLS NOT DISTINCT` on `start_at` (mirrors the `events` unique key; no `artist_id`), with table + column comments
- [x] 1.2 Register the migration file in `k8s/atlas/base/kustomization.yaml`; `atlas migrate apply --env local` + `validate` pass
- [x] 1.3 Add repository methods: insert/exists on `suppressed_concerts`

## 2. Backend — auto-publish branch in the discovery consumer

- [x] 2.1 In the discovery consumer, for a resolved venue run `resolveOrCreateVenue` → suppression gate → `detectDuplicateEvent` before persisting; an unresolved venue (`place == nil`) is staged (no auto-publish, no `venues` row)
- [x] 2.2 New concert (resolved venue, no conflict) → `buildAndInsertConcerts`, then publish `CONCERT.created`
- [x] 2.3 Conflict detected → upsert `staged_concert` (existing staging path), no publish
- [x] 2.4 Preserve the known-start "fill" path as new/publish, not a conflict
- [x] 2.5 Unit tests: new→auto-publish+event emitted; conflict→staged+no event; unresolved-venue→staged+no event+no venue; fill→publish; no orphan venue for staged-only

## 3. Backend — suppression + dedup + delete

- [x] 3.1 In the discovery consumer, after `resolveOrCreateVenue` yields `venue_id`, consult `suppressed_concerts` by the resolved `(venue_id, local_event_date, start_at)` key; a match skips the concert entirely (no auto-publish, no staging). The check sits in the consumer — not `FilterNew` — because `FilterNew` runs pre-venue-resolution on `(local_date, listed_venue_name)` and cannot key on `venue_id`
- [x] 3.2 In admin `Delete`, write a `suppressed_concerts` row (derived from the event's `venue_id`/`local_event_date`/`start_at`, regardless of how the concert was published) in the same transaction as the cascade delete
- [x] 3.3 Add a minimal un-suppress path (remove a `suppressed_concerts` row) for operator recovery
- [x] 3.4 Unit tests: suppressed key not re-created (auto nor staged); delete writes suppression; un-suppress re-enables discovery
- [x] 3.5 `make check` passes; open backend PR; merge

## 4. Ship to production & verify

> Note: 4.2/4.3 describe *observable* runtime behaviors that depend on Gemini surfacing a
> genuinely new concert / same-slot conflict on a discovery run. Shipped on backend v1.34.0
> (rolled forward to v1.35.0); the first prod discovery run on the new code (2026-08-17 09:00
> UTC) executed cleanly but deduped to "no new concerts" for every artist, so no auto-publish
> or conflict occurred to observe. The branch behavior is proven by the unit + integration
> tests; **live prod observation is deferred to organic discovery data** and not held as an
> archive blocker (accepted decision, 2026-08-18).

- [x] 4.1 Release backend (tag) → ArgoCD rollout; confirm migration applied and new consumer running
- [x] 4.2 Verify on next discovery run: a genuinely new concert auto-publishes + push fires; a same-slot conflict still lands in the approval queue — *shipped + proven by tests; live prod observation deferred to organic data (first run 2026-08-17 09:00 UTC found no new concerts)*
- [x] 4.3 Verify delete-with-suppression: delete an auto-published concert (via the existing admin `List` + `Delete`), confirm it is not re-created on the following discovery run — *shipped; `DeleteAndSuppress` + suppression gate proven by tests; live prod observation deferred to organic data*
