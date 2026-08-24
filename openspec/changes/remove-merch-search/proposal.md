## Why

The merch-url discovery feature delivers no reliable incremental value over the
concert `source_url` that discovery already captures, yet it costs a full extra
grounded Gemini call per series plus its own CronJob, DB column, proto field, and
fan-facing UI. Production data proves the redundancy: of the 117 series that carry
a `merch_url`, only **16%** share a host with the series' `source_url` (those are
the cases where merch resolved to the *same* tour feature page `source_url`
already points at), while **84%** resolved to a generic storefront top or bare
artist homepage — i.e. a link strictly *worse* than the tour-specific
`source_url` the fan already has. The tour feature page (`source_url`) contains
the goods section, so a separate merch link is either a duplicate or a
regression. Removing the feature simplifies the design across four repos and
removes ongoing Gemini/search cost for zero user-value loss.

## What Changes

- **BREAKING**: Remove the `Series.merch_url` field (proto field number `5`) from
  the published schema; reserve number `5` and name `merch_url` so the wire
  contract stays forward-safe.
- Retire the entire **merch-discovery** capability: the scheduled CronJob, the
  Gemini `MerchSearcher`, dead-link revalidation, candidate selection, and
  fill-once persistence.
- Drop the `series.merch_url` database column (new forward Atlas migration) and
  all read/write paths for it (repository queries, entity field, RPC mapper).
- Remove merch-searcher configuration (`GCP_GEMINI_MERCH_MODEL`,
  `GCP_GEMINI_MERCH_THINKING_LEVEL`, `GCP_MERCH_DISCOVERY_WINDOW`) and its
  defaults/accessors.
- Remove the fan-app "View Merch Info / グッズ情報を見る" link, its i18n keys, entity
  field, and store mapping.
- Remove the merch-discovery Kubernetes CronJob (base + dev/prod overlays), its
  ERROR-log Alert Policy, image build/deploy target, and prod image pin.
- **Keep (shared, not merch-owned)**: `GCP_GEMINI_SEARCH_API_KEY`,
  `GeminiSearchTemperature`, the `backend-app` service account, `backend-secrets`,
  the `gemini` Go package, and `series.source_url`.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `merch-discovery`: Retire the capability. All of its requirements (scheduled
  discovery job, candidate selection, dead-link revalidation, official-source
  Gemini resolution, fill-once persistence, job resilience) are REMOVED.
- `event-management`: Remove `merch_url` from the `Series` entity requirement and
  its two merch scenarios; `source_url` and the rest of the entity are unchanged.
- `concert-detail`: Remove the "Merch Info Link in Concert Detail" requirement
  and its scenarios; the official-info link is unchanged.
- `landing-page`: Remove the merchandise affordance from the interactive
  concert-detail requirement; official-info, venue, and calendar affordances stay.
- `gemini-searcher-config`: Remove the "GCPConfig exposes merch-searcher model and
  thinking fields" requirement (model/thinking env vars, defaults, accessors).
- `app-error-log-alerting`: Remove `merch-discovery` from the per-workload
  ERROR-log alert requirement and drop its dedicated scenario.

## Impact

Cross-repo, one-shot complete removal. Recommended ship order:

1. **cloud-provisioning** — remove the merch-discovery CronJob (base + overlays),
   its Alert Policy in `monitoring.ts`, and the prod image pin so nothing keeps
   populating `merch_url`.
2. **specification** — delete proto field `5`, reserve `5` + `merch_url`; expect
   `buf breaking` (FILE rule → `FIELD_NO_DELETE`) — the reserve is the standard
   mitigation; use the `buf skip breaking` PR label only if still flagged. Cut a
   BSR release.
3. **backend** — remove the job, use case, `MerchSearcher`, entity interfaces,
   mocks, repository queries, config, and the RPC mapper emit; drop the DB column
   via a new forward migration. The `DROP COLUMN` must land in the same release
   that stops reading `series.merch_url` (8 `concert_repo` SELECTs + mapper), or
   the fan-api query breaks.
4. **frontend** — after upgrading the generated schema package, remove the store
   mapping, entity field, detail-sheet link, and i18n keys. Readers use optional
   chaining, so an old client against a new backend degrades gracefully (the link
   simply never renders) — deploy sequencing risk is low.

No other consumers: there is no admin/organizer app dependency, and e2e carries no
merch tests. Merch discovery is a plain CronJob (no JetStream/KEDA), so there is
no shared-stream deletion hazard.
