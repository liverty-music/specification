## 1. Backend — venue get-or-create (A-1, no proto, ships first)

- [x] 1.1 Extract a single `admin_area` derivation helper (`resolved_admin_area ?? admin_area`) and use it for both the `(listed_venue_name, admin_area)` lookup and the insert in `internal/usecase/concert_admin_uc.go`
- [x] 1.2 In `resolveOrCreateVenue`, on `GetByPlaceID` miss fall back to `GetByListedName(listed_venue_name, admin_area)` before creating (covers the different-place_id case)
- [x] 1.3 Change `VenueRepository.Create` to `INSERT … ON CONFLICT DO NOTHING` (untargeted) with a re-SELECT by `google_place_id` then `(listed_venue_name, admin_area)` on suppressed insert; return the surviving row id in `internal/infrastructure/database/rdb/venue_repo.go` — this changes the method signature to return the id, so update the repo interface and the `createVenueFromStaged` caller
- [x] 1.4 Backfill `google_place_id` only when the found venue's value is NULL; never overwrite a non-NULL value. The backfill UPDATE cannot use untargeted `ON CONFLICT`, so catch a unique violation on `idx_venues_google_place_id` and degrade to a no-op (concurrent backfill)
- [x] 1.5 Unit/integration tests: different place_id → returns existing venue; concurrent create → single row; admin_area symmetry; NULL-only backfill (follow go-tester conventions, use local docker compose postgres)
- [x] 1.6 `make check` green; open backend PR for A-1 as a standalone fix

## 2. Backend — discovery dedup tolerates name drift (B, no proto)

- [x] 2.1 Add a venue-name normalization function (fold whitespace + full/half-width, strip leading `〈admin_area〉・` / `〈city〉公演 ＠` prefixes) with unit tests over the observed prod drift cases
- [x] 2.2 Apply normalization to the `listed_venue_name` component of the dedup key on BOTH sides of the comparison (scraped concert and the existing event/pending-staged name) in `entity.ScrapedConcerts.FilterNew` and the pending-staged dedup in `SearchNewConcerts`, keeping `(local_event_date, start_at)` unchanged
- [x] 2.3 Tests: prefixed vs unprefixed name dedups; genuinely different venues stay distinct; drifted name matches a pending staged row
- [x] 2.4 Confirm during implementation whether normalization alone clears the prod drift; if not, record the resolve-first-then-dedup fallback decision (design D2b) in this change — resolved: normalization (a) is sufficient, D2b deferred (design.md Open Questions)
- [x] 2.5 `make check` green; open backend PR for B (may bundle with A-1 or ship separately)

## 3. Specification — Approve RPC resolution + conflict (A-2 schema)

- [x] 3.1 Add a `resolution` enum (`RESOLUTION_UNSPECIFIED`, `KEEP_EXISTING`, `ADOPT_STAGED`) to the admin `ConcertService.Approve` request in the `rpc/admin/v1` proto
- [x] 3.2 Add a duplicate-conflict result to the `Approve` response carrying the existing event's display fields plus the staged preview; add protovalidate constraints; buf lint/format/breaking clean
- [x] 3.3 Open specification PR; after review + CI, merge and publish a GitHub Release to trigger BSR codegen (CI-only — do not run buf push/generate locally)
- [x] 3.4 Monitor `buf-release.yml` until BSR codegen completes

## 4. Backend — approval reconciliation (A-2, consumes generated types)

- [x] 4.1 Upgrade the generated schema package (`go get buf.build/gen/go/liverty-music/schema/...@vX.Y.Z`, `go mod tidy`)
- [x] 4.2 In the admin `Approve` handler + usecase, replace the zero-insert `FailedPrecondition` path: when a duplicate existing event is detected and `resolution` is unset, return the duplicate-conflict result without mutating
- [x] 4.3 Implement `KEEP_EXISTING`: append staged row to `rejected_concerts_log` with a duplicate reason and the calling reviewer's identity (thread reviewer id through the `Approve` handler like `Reject` already does), delete staged row, leave event unchanged
- [x] 4.4 Implement `ADOPT_STAGED`: overwrite existing event `listed_venue_name`, fill `start_at`/`open_at` via COALESCE only where currently NULL (never null out a known time), leave `venue_id`/`google_place_id` and the shared `series.title` unchanged, delete staged row
- [x] 4.5 Ensure two-phase idempotency: second call re-reads the staged row and re-checks the conflict; missing staged row hits the existing "already approved" success path
- [x] 4.6 Tests for all three resolution paths + no-choice conflict; `make check` green

## 5. Frontend — reconciliation dialog (A-2, consumes generated types)

- [x] 5.1 Upgrade the generated schema package (`npm install @buf/liverty-music_schema.connectrpc_es@latest`)
- [x] 5.2 In the admin console approval action, when `Approve` returns a duplicate-conflict, open a record-level dialog showing existing vs staged (venue display name, start/open time, title)
- [x] 5.3 Wire the two choices to re-call `Approve` with `KEEP_EXISTING` / `ADOPT_STAGED`; refresh the queue on success
- [x] 5.4 Component/e2e coverage per frontend testing conventions; `make check` green

## 6. Release & prod verification

- [x] 6.1 Release backend A-1/B; verify in prod that 和歌山ビッグホエール approves without `already_exists` and drift duplicates dedup at discovery
- [x] 6.2 Release backend A-2 + frontend A-2 (after BSR); verify the reconciliation dialog end to end in prod (keep-existing clears + logs; adopt-staged updates display fields)
- [x] 6.3 Decide and execute cleanup of the existing ~19 stale staged rows (via the new reconciliation path or manual review); confirm the pending queue no longer holds unapprovable duplicates — resolved: reviewer cleared the 18 stale rows via the live admin-console reconciliation dialog (2026-07-27), queue confirmed clean
