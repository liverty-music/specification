## Why

The `concert-discovery` CronJob calls the Gemini search API (a grounded two-step
pipeline whose Step 1 is the dominant cost) once per followed artist on every run.
Empirically most of these calls are wasteful: in a representative prod run only a
small fraction yielded any new concert, and for Japanese artists tour line-ups are
typically announced as a single batch and then stay quiet for weeks. Re-searching an
artist a day after a discovery just re-finds the same concerts and dedups to nothing.
With a small user base today, notification latency is cheap and Gemini cost is the
priority — so we can safely skip more aggressively.

## What Changes

- Make the search-freshness TTL **configurable** instead of a hard-coded 24h constant,
  and set **prod = 72h** (dev stays at the 24h default). An artist searched within the
  TTL is skipped, as today — just with a longer window in prod.
- Add a new skip condition: **skip the external search if a new concert was discovered
  for the artist within the last 14 days.** The 14-day window is **env-configurable**
  (default 14d). This requires tracking *when* an artist last yielded a new concert, which
  is not recorded anywhere today.
- Record a `last_found_at` timestamp on the artist's search log whenever a search
  publishes at least one genuinely new (post-dedup) concert.

Out of scope (future, separate changes): follower-weighted search cadence, and
official-site change-detection as a search trigger.

## Capabilities

### New Capabilities

(none — all behavior modifies existing capabilities)

### Modified Capabilities

- `concert-search`: the "Search Concerts by Artist" skip rule changes — the freshness
  window becomes configurable (default 24h) rather than a fixed 24h, and a second skip
  condition is added (skip when a new concert was discovered within the last 14 days).
- `concert-search-log`: the `latest_search_logs` schema gains a nullable `last_found_at`
  column, and a new tracking rule records it when a search discovers new concerts.
- `gemini-searcher-config`: two new env-configurable settings are added — the
  search-cache TTL and the recent-discovery skip window — each resolved with env-var
  precedence over a built-in default, following the existing per-step model-resolution
  pattern.

## Impact

- **backend**
  - `pkg/config`: new TTL env field on `JobConfig`/`GCPConfig` with default + validation.
  - `internal/usecase/concert_uc.go`: TTL **and** discovery window sourced from config
    (not the `searchCacheTTL` constant); new "discovered within window" skip branch in
    `SearchNewConcerts`; `executeSearch` updates `last_found_at` when post-dedup new
    concerts are published.
  - `internal/entity/search_log.go`: `SearchLog` gains `LastFoundTime`; new helper for
    the discovery-recency check.
  - `internal/infrastructure/database/rdb`: search-log repository reads/writes
    `last_found_at`; new Atlas migration adding the nullable column.
  - tests: usecase + repository + entity unit tests updated for the new branch/column.
- **cloud-provisioning**
  - prod `concert-discovery` Kustomize `configmap.env` sets the TTL env to 72h (and
    optionally the discovery-window env); dev unchanged. Non-secret tuning stays on the
    existing configmap.env path — Pulumi/ESC is not involved (it manages secrets only).
- **Deployment**: ships through backend Release → prod AR pin bump → ArgoCD sync, plus
  the Atlas Operator applying the new migration before the CronJob picks it up.
- **No proto/BSR change** — purely backend behavior + infra config.
