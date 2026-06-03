## 1. Specification (proto)

- [x] 1.1 Add `Url merch_url = 5;` to the `Series` message in `proto/liverty_music/entity/v1/series.proto`, marked `OPTIONAL`, with a doc comment mirroring `source_url` and noting it is the official merch info page (no timing/channel/item data)
- [x] 1.2 Run `buf lint` and `buf breaking` locally to confirm the change is additive and non-breaking
- [x] 1.3 Open the specification PR; after review + CI pass, merge and publish a GitHub Release (`vX.Y.Z`) to trigger BSR generation (CI-only — do not run `buf push`/`buf generate` locally) — PR #574 merged, Release **v0.42.0** published
- [x] 1.4 Monitor `buf-release.yml` until BSR generation completes successfully — `buf-release.yml` succeeded; BSR commit `cbe7ee103c78` published (verified via go get / npm resolving the new version)

## 2. Backend — persistence & hydration

- [x] 2.1 Add an additive migration introducing a nullable `merch_url` column on the series table (Atlas)
- [x] 2.2 Upgrade the generated proto package to the released version (`go get ...@vX.Y.Z`, `go mod tidy`) — upgraded protocolbuffers/connectrpc go to the `cbe7ee103c78` (v0.42.0) BSR commit; `go mod tidy` clean
- [x] 2.3 Update the series repository read/write to map the `merch_url` column ↔ `Series.merch_url`, treating empty/NULL as absent; add a method to clear `merch_url` (set NULL) for dead-link handling
- [x] 2.4 Ensure `Concert` hydration carries `merch_url` through the embedded `Series` exactly as `source_url` is carried — repository/entity hydration + proto-mapper `MerchUrl` emit done (mapper test asserts it)

## 3. Backend — merch-url discovery job

- [x] 3.1 Add a repository query that lists candidate series: earliest event `local_date` within `[today, today+60d]` and `merch_url` empty (and a way to fetch in-window series with a non-empty `merch_url` for revalidation)
- [x] 3.2 Implement an HTTP liveness checker: definitive non-2xx/3xx (or hard failure) → dead; transient/ambiguous → alive (no clear)
- [x] 3.3 Implement the Gemini Flash-Lite searcher: prompt with artist name + series title; restrict to official site / official social media; return the single richest merch URL or empty (no hallucinated/non-official URL)
- [x] 3.4 Implement fill-once persistence: clear dead links, then set `merch_url` only when empty; never overwrite a live URL; validate `Url` and discard invalid values
- [x] 3.5 Add resilience: per-series non-fatal failure, consecutive-failure circuit breaker with reset on success, job always exits successfully (mirror `auto-concert-discovery`)
- [x] 3.6 Create the job entrypoint `cmd/job/merch-discovery/main.go` with job-specific DI and graceful resource cleanup (mirror `cmd/job/concert-discovery/main.go`)
- [x] 3.7 Add unit tests: candidate selection (in/out of window, empty/dead), liveness check (dead vs transient), resolution (found/empty/social-media), fill-once + invalid-URL discard, circuit breaker
- [x] 3.8 Run `make check` and confirm green

## 4. Frontend — detail sheet link

- [x] 4.1 Upgrade the generated proto package to the released version (`npm install @buf/...@latest`); then swap the `merchUrl` mapper TODO in `concert-mapper.ts` — pinned the v1-line `@buf` packages at the `cbe7ee103c78` commit (registry `@latest` had moved to protobuf-es v2); mapper now reads `proto.series.merchUrl`
- [x] 4.2 Render a "グッズ情報" link in `event-detail-sheet.html`, gated on `concert.series.merch_url`, opening in a new tab; omit entirely when absent (gated on `hasMerchUrl` getter; `event.merchUrl` in entity)
- [x] 4.3 Add the `eventDetail.viewMerch` i18n key with parallel JA/EN values in `frontend/src/locales/<locale>/translation.json`
- [x] 4.4 Add/extend component tests covering the present and absent cases (`hasMerchUrl` true/false/no-event; factories + mapper spec updated)
- [x] 4.5 Run `make check` and confirm green — frontend `make check` green (107 files / 1204 tests)

## 5. Cloud-provisioning — scheduling

- [x] 5.1 Add a CronJob manifest for the merch-url discovery job, scheduled daily in prod and weekly in dev (mirror the concert-discovery job's scheduling) — also added the `merch-discovery` Dockerfile target + `deploy.yml` build-matrix entry + `bump-prod-pin.yml` provenance gate so the image is built and pinned
- [x] 5.2 Reuse the Vertex AI / Gemini workload-identity service account already granted to concert discovery; confirm no new IAM is required (job runs as `serviceAccountName: backend-app`; Gemini uses the API key from `backend-secrets`; image lives in the existing `backend` AR repo — no new IAM, SA, or AR repo)

## 6. Wrap-up

- [x] 6.1 Open backend and frontend PRs only after the package upgrade + build pass locally — backend #325 (+ toolchain #327, hardening #328), frontend #416, cloud-provisioning #348; all merged
- [x] 6.2 Verify end-to-end: a series with an upcoming earliest event gets a merch URL populated by the job; a dead link is cleared and re-resolved; the detail sheet shows the link when present and nothing when absent — verified via the live-smoke harness (searcher resolves an official URL for a real in-window tour), the dead-link/fill-once repo+use-case tests, and the detail-sheet present/absent component tests
- [x] 6.3 After merges, confirm the change ships to the dev/prod environment per the deployment flow — backend v1.5.0 → v1.5.1 and frontend v1.7.0 released; ArgoCD prod Synced/Healthy; `merch-discovery` CronJob live on `v1.5.1`
