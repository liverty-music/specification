## 1. Specification (proto / BSR)

- [ ] 1.1 Add `origin` (enum: `auto_published` / `admin_approved`) and `auto_published_at` fields to the admin `ConcertService.List` concert message in `rpc/admin/v1`
- [ ] 1.2 `buf lint` + `buf format -w` + `buf breaking` pass (fields are additive; no breaking label expected)
- [ ] 1.3 Open specification PR, merge, publish GitHub Release (vX.Y.Z), confirm `buf-release.yml` pushes to BSR

## 2. Backend — data model

- [ ] 2.1 Atlas migration: add `events.origin` (NOT NULL, default `admin_approved` for existing rows) and nullable `events.auto_published_at` (`TIMESTAMPTZ`)
- [ ] 2.2 Atlas migration: create `suppressed_concerts` keyed by the event triple `(venue_id, local_event_date, start_at)` with `NULLS NOT DISTINCT` on `start_at` (mirrors the `events` unique key; no `artist_id`)
- [ ] 2.3 Register both migration files in `k8s/atlas/base/kustomization.yaml`; `atlas migrate apply --env local` + `validate` pass
- [ ] 2.4 Add repository methods: insert/exists on `suppressed_concerts`; set `origin`/`auto_published_at` on event insert

## 3. Backend — auto-publish branch in the discovery consumer

- [ ] 3.1 In `concert_creation_uc.go`, resolve/create venue and run `detectDuplicateEvent` before persisting
- [ ] 3.2 New concert (no conflict) → `buildAndInsertConcerts` with `origin=auto_published` + `auto_published_at`, then publish `CONCERT.created`
- [ ] 3.3 Conflict detected → upsert `staged_concert` (existing staging path), no publish
- [ ] 3.4 Preserve the known-start "fill" path as new/publish, not a conflict
- [ ] 3.5 Set `origin=admin_approved` on the approval insert path in `concert_admin_uc.go`
- [ ] 3.6 Unit tests: new→auto-publish+event emitted; conflict→staged+no event; fill→publish; no orphan venue for staged-only

## 4. Backend — suppression + dedup + delete

- [ ] 4.1 Extend `FilterNew` (`concert_uc.go`) to exclude natural keys present in `suppressed_concerts` (third source alongside published + pending)
- [ ] 4.2 In admin `Delete`, write a `suppressed_concerts` row (derived from the event's `venue_id`/`local_event_date`/`start_at`, origin-agnostic) in the same transaction as the cascade delete
- [ ] 4.3 Add a minimal un-suppress path (remove a `suppressed_concerts` row) for operator recovery
- [ ] 4.4 Map `origin` + `auto_published_at` into the admin `List` RPC response
- [ ] 4.5 Unit tests: suppressed key not re-created (auto nor staged); delete writes suppression; un-suppress re-enables discovery; `List` carries origin/time
- [ ] 4.6 `make check` passes; open backend PR after BSR gen; merge

## 5. Frontend — admin console review view

- [ ] 5.1 Upgrade the generated schema package to the released version; swap to generated `origin`/`auto_published_at` types
- [ ] 5.2 Add a "recently auto-published" review view: client-side filter `origin=auto_published AND auto_published_at >= now - window` (default 7 days, configurable)
- [ ] 5.3 Items age out of the view automatically (no acknowledgement); each row has a delete action calling admin `Delete`
- [ ] 5.4 Ensure the concert-detail deep-link degrades gracefully when the target event was deleted
- [ ] 5.5 `make check` passes; open frontend PR after BSR gen; merge

## 6. Ship to production & verify

- [ ] 6.1 Release backend (tag) → ArgoCD rollout; confirm migration applied and new consumer running
- [ ] 6.2 Release frontend (GH Release → pin-bump) → confirm review view live in admin console
- [ ] 6.3 Verify on next discovery run: a genuinely new concert auto-publishes + push fires; a same-slot conflict still lands in the approval queue
- [ ] 6.4 Verify delete-with-suppression: delete an auto-published concert, confirm it is not re-created on the following discovery run
