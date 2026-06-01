## Context

`SearchNewConcerts` (`backend/internal/usecase/concert_uc.go`) gates the Gemini search
behind a single freshness check: `SearchLog.IsFresh(now, searchCacheTTL)` where
`searchCacheTTL` is a compile-time constant `24 * time.Hour`, shared by all
environments. The CronJob runs daily in prod (`0 9 * * *`), so each followed artist is
re-searched roughly every 24h whether or not anything changed.

Cost is dominated by Step 1 of the searcher (grounded GoogleSearch + URLContext +
medium/high thinking). Skipping a search saves a whole Step 1 + Step 2 pass.

The data layer can answer "when did we last *search*?" (`latest_search_logs.searched_at`)
but **not** "when did we last *discover something new*?" — there is no discovery
timestamp on `latest_search_logs`, and `events` has no `created_at` column (its `id` is
UUIDv7 but reconstructing discovery time through the series→performer join is brittle and
unsuitable as a primary signal).

## Goals / Non-Goals

**Goals:**
- Reduce Gemini API spend by skipping searches that are very unlikely to yield new data.
- Make the freshness TTL environment-configurable; set prod to 72h, keep dev at 24h.
- Add a "skip if a new concert was discovered within the last 14 days" condition, backed
  by a first-class discovery timestamp.
- Ship to prod (config + migration + release), not just merge.

**Non-Goals:**
- Follower-weighted / engagement-weighted cadence (future change).
- Official-site change-detection as a search trigger (future change).
- Failed-search backoff — rejected: prod failures are currently ~zero and error alerting
  already provides detection; backoff would solve a non-problem and add complexity.
- Resetting to a *shorter* interval immediately after a discovery — rejected: for the
  batch-then-quiet (Japanese tour) announcement pattern, a fresh discovery predicts
  *quiet*, not more activity, so we lengthen rather than shorten after a hit.

## Decisions

### D1: Configurable TTL and discovery window via env (default 24h / 14d, prod 72h)

Replace the `searchCacheTTL` constant with config-sourced values. Add two `time.Duration`
env fields resolved with env-precedence-over-default, mirroring the existing
`SearchModelExtract()` / `SearchModelParse()` helpers in `gemini-searcher-config`:

- `GCP_GEMINI_SEARCH_CACHE_TTL` — freshness window, default `24h`.
- `GCP_GEMINI_SEARCH_DISCOVERY_WINDOW` — recent-discovery skip window, default `336h` (14d).

The prod `concert-discovery` configmap sets `CACHE_TTL=72h` (and may set the discovery
window explicitly to `336h` for visibility, or omit it to inherit the default); dev omits
both and inherits the defaults.

- *Alternative considered*: change the constant to 72h globally. Rejected — prod-specific
  tuning is wanted, and a config knob lets us tune per-env without a code release.
- *Alternative considered*: keep the 14d window a code constant. Rejected per decision to
  env-configure it from the start, so the window can be tuned without a backend release.
- *Alternative considered*: make these `JobConfig` top-level fields rather than under
  `GCPConfig`. Either works; placing them alongside the other Gemini-search settings keeps
  the searcher-config capability cohesive.

### D2: Track discovery time with a nullable `last_found_at` column

Add `last_found_at TIMESTAMPTZ NULL` to `latest_search_logs`. It is set to "now" only
when a search publishes ≥1 genuinely new concert (i.e. `FilterNew` returns a non-empty
set in `executeSearch`). NULL means "never discovered anything yet" → the discovery-skip
never fires for that artist.

- *Alternative considered*: derive discovery time from `events.id` UUIDv7 via
  series→performer join. Rejected — brittle, couples the skip logic to ID-encoding
  details and the dedup/UPSERT id-stability behavior; a dedicated column is explicit and
  cheap. (`auto-concert-discovery` already keeps a discovery-skip concern out of the
  event table.)
- *Alternative considered*: a separate `concert_discoveries` audit table. Rejected —
  over-engineered for a single "last" timestamp; the search log is already the per-artist
  cadence record.

### D3: Two independent skip gates, OR-combined

`SearchNewConcerts` skips the external call when **either**:
1. `IsFresh(now, ttl)` — recently *searched* (existing behavior, now configurable), **or**
2. `last_found_at` is set **and** `now - last_found_at < discoveryWindow` — recently *discovered*.

The pending/in-progress guard (`IsPending`) is unchanged. Both the TTL **and** the
discovery window are env-configurable from day one (see D5), each with a built-in default
(24h and 14d=336h respectively). Both gates are advisory caches over the same source of
truth, so OR is correct: any reason to believe "nothing new soon" suppresses the call.

### D4: Skip vs. fresh-status interaction

The discovery-skip only consults `last_found_at`; it does not require `status =
completed`. But because `last_found_at` is only ever written on a successful discovery,
its presence already implies a past completed run. A `failed` newer run does not clear
`last_found_at` (we keep the last *successful* discovery time), which is the intended
behavior — a transient failure should not force a re-search storm inside the 14-day
window.

### D5: Config delivery via Kustomize configmap.env (not Pulumi/ESC)

Both knobs are non-secret tuning values, so they follow the established split: Pulumi
(`cloud-provisioning/src/`) manages GCP infra + GSM secrets only (it creates **zero** k8s
ConfigMaps today), while non-secret cronjob env lives in committed Kustomize
`configmap.env` overlays. The new env vars are set in the prod `concert-discovery`
configmap; dev inherits the code defaults.

- *Alternative considered*: define the values in Pulumi ESC and have Pulumi render a new
  k8s ConfigMap. Rejected — introduces a brand-new "Pulumi owns a backend ConfigMap"
  pattern for a plain tuning value; the existing configmap.env path is simpler and
  consistent with every other non-secret cronjob env.
- *Alternative considered*: ESC → GSM → ExternalSecret (the API-key path). Rejected —
  these are not secrets; treating them as such is a category error.

## Risks / Trade-offs

- **Delayed notification for incremental tour adds** → For artists who *do* add dates
  within 14 days of a first announcement, the new date is detected up to ~14 days late.
  Mitigation: acceptable given the current tiny user base and cost priority; the window
  is a single constant we can shorten quickly, and TTL/config is env-tunable without a
  migration.
- **`last_found_at` semantics drift** → If `executeSearch`'s "new concert" definition
  (post-`FilterNew`) changes, the discovery signal changes with it. Mitigation: write
  `last_found_at` at exactly the same point we publish `concert.discovered`, so the
  column tracks "we emitted a discovery event," which is the meaningful definition.
- **Migration ordering** → The backend code reading `last_found_at` must not roll out
  before the column exists. Mitigation: Atlas Operator sync-wave ordering already
  sequences `backend-migrations` ahead of the backend workloads (per backend CLAUDE.md);
  the new column is nullable and additive, so an old binary tolerates it too.
- **Duration parsing** → A malformed `GCP_GEMINI_SEARCH_CACHE_TTL` or
  `GCP_GEMINI_SEARCH_DISCOVERY_WINDOW` must fail fast. Mitigation: parse + validate in
  `JobConfig.Validate()` like the existing thinking-level validation.

## Migration Plan

1. Backend PR: config field + entity field + usecase skip branch + repo read/write +
   Atlas migration (`add_last_found_at_to_search_logs`) registered in the migrations
   kustomization; unit tests. `make check` green.
2. Merge backend PR → cut backend Release `vX.Y.Z` → prod AR pin bump → ArgoCD sync.
3. cloud-provisioning PR: prod `concert-discovery` configmap adds the 72h TTL env (and the
   discovery-window env); bump the prod image pin to `vX.Y.Z`. Atlas Operator applies the
   migration ahead of the CronJob.
4. Verify in prod: next CronJob run logs show the new skip branch firing; `latest_search_logs`
   shows `last_found_at` populated after a discovery.

**Rollback**: revert the configmap/pin PR (TTL + window fall back to defaults; old binary
ignores the column). The additive nullable column needs no down-migration.

## Open Questions

- Confirm whether the TTL/window knobs belong on `GCPConfig` (cohesive with searcher
  settings) vs. `JobConfig` top-level — minor, settle during implementation.
- (Resolved) Discovery window is env-configurable from day one; config delivery is via
  Kustomize configmap.env, not Pulumi/ESC.
