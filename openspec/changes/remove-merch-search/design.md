## Context

See proposal.md — Why. The merch-url feature spans four repos and the BSR schema: a standalone Kubernetes CronJob (`merch-discovery`, no JetStream/KEDA), the `MerchSearcher` Gemini call, the `series.merch_url` column read all the way through to a fan-facing detail link. `series.merch_url` is not write-only — `concert_repo` SELECTs it (8 queries) and the RPC mapper serializes it to `Series.merch_url` (proto field `5`), which the fan PWA renders. Removal is therefore a coordinated cross-repo change, not an internal cleanup.

Shared surfaces that merch happens to touch but MUST be retained: `GCP_GEMINI_SEARCH_API_KEY`, `GCP_GEMINI_SEARCH_TEMPERATURE`, the `backend-app` service account, `backend-secrets`, the `gemini` Go package, and `series.source_url`.

## Goals / Non-Goals

**Goals:**
- Delete the merch feature completely in one coordinated rollout, leaving no dead field, column, job, config, or UI.
- Keep the proto wire contract forward-safe (reserve the field number/name).
- Order the DB column drop so the fan API never queries a missing column.

**Non-Goals:**
- No replacement merch capability. The tour feature page reached via `series.source_url` already surfaces goods information.
- No change to `series.source_url` or the concert/sales-phase discovery jobs.
- The unrelated series-fragmentation issue (one series per event) is out of scope.

## Decisions

- **Reserve the proto field rather than hard-delete it.** Removing `Series.merch_url = 5` is breaking under buf's `FILE` rule (`FIELD_NO_DELETE`). Reserve number `5` and name `merch_url` so the number is never reused and downstream regeneration stays clean. Alternative (leave the field, stop populating) was rejected: it keeps dead surface in the schema and the fan client, contradicting the "delete everything" goal. If `buf breaking` still flags the reserved deletion, use the repo's `buf skip breaking` PR label.
- **Drop the DB column in a follow-up release, not with the read-path removal (expand/contract).** The backend Deployment rolls with `maxUnavailable: 0`, so the OLD pods keep serving fan-api traffic — still issuing the 8 `concert_repo` SELECTs on `s.merch_url` — until the new pods pass readiness. The Atlas operator runs migrations ahead of the Deployment on the same sync, so dropping the column in the read-path-removal release would break those still-running old pods with `column "merch_url" does not exist`. Split it: **release A** removes the read/write path (SELECTs, mapper emit, writes) while the column stays; once A is fully rolled out, **release B** applies the `ALTER TABLE series DROP COLUMN merch_url` forward migration (nothing references the column by then). Historical migrations (including `20260605...rework...`, which references the column in an applied data-migration) are never edited, preserving the `atlas.sum` chain.
- **One-shot across repos, except the DB column (expand/contract).** The frontend reader uses optional chaining, so an old client against a new backend simply stops rendering the link — cross-repo deploy-sequencing risk is low, and the schema/BSR/backend/frontend removals can proceed on the standard dependency order. The single exception is the `series.merch_url` column, which needs the two-release expand/contract above so in-flight old pods never query a dropped column.
- **Delete `httpx/liveness.go` outright.** It is the SSRF-hardened probe used only by merch dead-link revalidation; no other feature imports it today. If a future feature wants a generic liveness probe it can be reintroduced; carrying dead code now violates the simplicity goal.
- **Retire `merch-discovery` as a capability.** Its six requirements are REMOVED wholesale rather than modified — the capability ceases to exist.

## Risks / Trade-offs

- [Column drop breaks old pods mid-rollout] → Expand/contract: release A removes the read/write path with the column still present; a later release B drops the column once A is fully deployed. Never drop the column in the same release that still reads it (`maxUnavailable: 0` keeps old pods serving during the roll).
- [`buf breaking` blocks the schema PR] → Reserve field 5 + name; if still flagged, apply the `buf skip breaking` label (documented escape hatch).
- [CronJob keeps writing `merch_url` during the transition] → Remove the CronJob first (cloud-provisioning), before the column drop, so nothing repopulates it.
- [OpenSpec 1.8 cannot forward-delta a partial scenario drop] → The two `Series` merch scenarios and the merch-discovery alert scenario are carried as `**REMOVED**` tombstones in the MODIFIED blocks; delete them from the main specs during archive (matches the project's existing scenario-hygiene practice).
- [Stale prod data] → Existing `merch_url` values disappear with the column; acceptable, since the feature is being retired and the values were low-quality (see proposal.md).

## Migration Plan

Ship order (each step is its own PR / deploy):

1. **cloud-provisioning** — delete the `merch-discovery` CronJob (base + dev/prod overlays), its Alert Policy in `monitoring.ts`, and the prod image pin. This stops any run from repopulating `merch_url`.
2. **specification** — delete proto field 5, add `reserved 5; reserved "merch_url";`; merge → GitHub Release → BSR gen.
3. **backend (release A)** — remove the job, use case, searcher, entity interfaces/field, mocks, repo queries (SELECT + write paths), config, and the RPC mapper emit; upgrade to the new BSR types. The `series.merch_url` column REMAINS in this release.
4. **frontend** — upgrade the generated schema package, then remove the store mapping, entity field, detail-sheet link, `hasMerchUrl` gate, and the `eventDetail.viewMerch` i18n keys.
5. **backend (release B)** — once release A is fully rolled out (no pod still reads `merch_url`), add and apply the `ALTER TABLE series DROP COLUMN merch_url` forward migration.

Rollback: revert per-repo PRs. The DB column drop (release B) is the only hard-to-reverse step — a rollback would re-add the column (empty) via a new migration; acceptable because nothing depends on historical values.
