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
- **Drop the DB column in the same backend release that removes its read path.** `concert_repo` SELECTs `s.merch_url` and the mapper emits it; the Atlas operator runs the `DROP COLUMN` migration ahead of the Deployment on the same sync. If the new binary still referenced the column after the drop, the fan-api query would break. So the column drop and the read-path removal ship together. A new forward migration (`ALTER TABLE series DROP COLUMN merch_url`) is added; historical migrations (including `20260605...rework...` which references the column in an applied data-migration) are never edited, preserving the `atlas.sum` chain.
- **One-shot complete removal, not phased.** The frontend reader uses optional chaining, so an old client against a new backend simply stops rendering the link — deploy-sequencing risk is low enough to do it all at once across the standard dependency order (schema → BSR → backend + frontend).
- **Delete `httpx/liveness.go` outright.** It is the SSRF-hardened probe used only by merch dead-link revalidation; no other feature imports it today. If a future feature wants a generic liveness probe it can be reintroduced; carrying dead code now violates the simplicity goal.
- **Retire `merch-discovery` as a capability.** Its six requirements are REMOVED wholesale rather than modified — the capability ceases to exist.

## Risks / Trade-offs

- [Column drop lands before code stops reading it] → Ship the read-path removal and the `DROP COLUMN` migration in the same backend release; the Atlas operator's sync-wave ordering runs the migration before the new Deployment.
- [`buf breaking` blocks the schema PR] → Reserve field 5 + name; if still flagged, apply the `buf skip breaking` label (documented escape hatch).
- [CronJob keeps writing `merch_url` during the transition] → Remove the CronJob first (cloud-provisioning), before the column drop, so nothing repopulates it.
- [OpenSpec 1.8 cannot forward-delta a partial scenario drop] → The two `Series` merch scenarios and the merch-discovery alert scenario are carried as `**REMOVED**` tombstones in the MODIFIED blocks; delete them from the main specs during archive (matches the project's existing scenario-hygiene practice).
- [Stale prod data] → Existing `merch_url` values disappear with the column; acceptable, since the feature is being retired and the values were low-quality (see proposal.md).

## Migration Plan

Ship order (each step is its own PR / deploy):

1. **cloud-provisioning** — delete the `merch-discovery` CronJob (base + dev/prod overlays), its Alert Policy in `monitoring.ts`, and the prod image pin. This stops any run from repopulating `merch_url`.
2. **specification** — delete proto field 5, add `reserved 5; reserved "merch_url";`; merge → GitHub Release → BSR gen.
3. **backend** — remove the job, use case, searcher, entity interfaces/field, mocks, repo queries, config, and the RPC mapper emit; add the `DROP COLUMN merch_url` forward migration in the same release (read-path removal + drop together). Upgrade to the new BSR types.
4. **frontend** — upgrade the generated schema package, then remove the store mapping, entity field, detail-sheet link, `hasMerchUrl` gate, and the `eventDetail.viewMerch` i18n keys.

Rollback: revert per-repo PRs. The DB column drop is the only hard-to-reverse step — a rollback would re-add the column (empty) via a new migration; acceptable because nothing depends on historical values.
