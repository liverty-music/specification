## 1. Backend — config (TTL + discovery window)

- [x] 1.1 Add a search-cache TTL env field (`GCP_GEMINI_SEARCH_CACHE_TTL`, `time.Duration`) to the job config in `pkg/config/config.go`, with a 24h default
- [x] 1.2 Add a discovery-window env field (`GCP_GEMINI_SEARCH_DISCOVERY_WINDOW`, `time.Duration`), with a 336h (14d) default
- [x] 1.3 Add resolver helpers for both (env-precedence over default) following the `SearchModelExtract()` / `SearchModelParse()` pattern
- [x] 1.4 Validate both durations in `JobConfig.Validate()` so a non-parseable value fails fast at startup
- [x] 1.5 Add/extend config unit tests (`pkg/config/config_test.go`) for override, default, and invalid value (both fields)

## 2. Backend — search log entity & schema

- [x] 2.1 Add `LastFoundTime time.Time` (nullable) to `SearchLog` in `internal/entity/search_log.go`
- [x] 2.2 Add a helper (e.g. `WasRecentlyDiscovered(now, window) bool`) returning false when `LastFoundTime` is zero/null
- [x] 2.3 Add the desired-state column `last_found_at TIMESTAMPTZ NULL` to `internal/infrastructure/database/rdb/schema/schema.sql` (+ COMMENT)
- [x] 2.4 Add the Atlas migration `20260601120000_add_last_found_at_to_search_logs.sql` (hand-authored to match schema.sql + `atlas migrate hash`; `atlas migrate diff` blocked locally by the ephemeral dev-DB `app` search_path snapshot)
- [x] 2.5 Register the new migration file in `k8s/atlas/base/kustomization.yaml` under `configMapGenerator.files`
- [x] 2.6 Add entity unit tests for the discovery-recency helper (null, within window, outside window)

## 3. Backend — repository

- [x] 3.1 Update the search-log repository to read `last_found_at` in `GetByArtistID`
- [x] 3.2 Add a method to set `last_found_at = now` for an artist (or extend Upsert/UpdateStatus) without disturbing `searched_at` semantics
- [x] 3.3 Update repository integration tests for read + discovery-time write

## 4. Backend — use case wiring

- [x] 4.1 Thread the configured TTL and discovery window from `JobConfig` into the concert use case (via DI in `internal/di/job.go` and the server provider if shared); remove the hard-coded `searchCacheTTL` constant
- [x] 4.2 Add the discovery-recency skip branch in `SearchNewConcerts`: OR-combine `IsFresh(now, ttl)` with `WasRecentlyDiscovered(now, discoveryWindow)` using the configured window
- [x] 4.3 In `executeSearch`, set `last_found_at = now` exactly when post-`FilterNew` new concerts are published (same point as the `concert.discovered` publish)
- [x] 4.4 Update use case unit tests: skip-on-recent-discovery, no-skip-when-null, TTL honoured, discovery recorded only on non-empty new set
- [x] 4.5 `make check` passes (lint + unit/integration tests)

## 5. cloud-provisioning — prod config

- [x] 5.1 Add `GCP_GEMINI_SEARCH_CACHE_TTL=72h` (and optionally `GCP_GEMINI_SEARCH_DISCOVERY_WINDOW=336h` for visibility) to the prod `concert-discovery` Kustomize configmap (`k8s/namespaces/backend/overlays/prod/cronjob/concert-discovery/configmap.env`); leave dev unset (inherits defaults). Pulumi/ESC not involved — non-secret tuning stays on the configmap.env path
- [x] 5.2 `kubectl kustomize k8s/namespaces/backend/overlays/prod` renders cleanly; `make check` passes

## 6. Ship to prod

- [x] 6.1 Open + merge the backend PR (CI green) per cross-repo workflow
- [x] 6.2 Cut a backend GitHub Release `vX.Y.Z`; confirm prod AR images pushed
- [x] 6.3 Open + merge the cloud-provisioning PR (prod image pin bump to `vX.Y.Z` + TTL configmap)
- [x] 6.4 Confirm Atlas Operator applies the `last_found_at` migration ahead of the backend/CronJob rollout
- [x] 6.5 Verify in prod: a CronJob run logs the new skip branch firing, and `latest_search_logs.last_found_at` is populated after a discovery
