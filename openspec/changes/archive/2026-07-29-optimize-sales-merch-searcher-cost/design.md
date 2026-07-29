## Context

`sales-phase-discovery` and `merch-discovery` both run the Gemini searcher on `gemini-3.1-flash-lite`. Post-concert-migration, they are the remaining "search query gemini 3 paid" cost (~¥448/day, ~2x fan-out). The `optimize-concert-searcher-cost` change proved that `gemini-3.6-flash` (a) grounds correctly while reporting `tool_use=0`/`webSearchQueries=0` in metadata (verified via post-cutoff data), and (b) bills that grounding as cheap tokens rather than per-search-query fan-out.

Constraint: metadata cannot be trusted to judge grounding (see the concert change) — quality is judged by whether the searcher extracts **post-training-cutoff** data.

## Goals / Non-Goals

**Goals:**

- Migrate `sales-phase-discovery` and `merch-discovery` extract to `gemini-3.6-flash` + thinking `medium`.
- Improve grounding quality (flash-lite under-grounds sales phases and hallucinates merch URLs).
- Reduce the remaining per-search-query billing to token billing.
- Keep the change lean: merch = code default change; sales = prod-overlay env change; both inherit the concert change's `defaultSearchModelExtract`.

**Non-Goals:**

- No change to `ConcertSearcher` (already 3.6-flash) or the email parser (Vertex, no grounding).
- Step 2 parse stays `gemini-3.1-flash-lite` (mechanical JSON coercion; schema-bounded).
- No proto/API change.

## Decisions

### D1: merch default model `gemini-3.1-flash-lite` → `gemini-3.6-flash`, thinking `high` → `medium`

merch has no env override, so changing the code defaults migrates it. A/B evidence below.

### D2: sales-phase extract → `gemini-3.6-flash`, thinking `high` → `medium`

sales-phase overrides the extract model to flash-lite via its configmap; switching that env (or dropping it to inherit the `gemini-3.6-flash` default) migrates it with no backend code change. Parse stays flash-lite.

### D3: thinking = `medium` (fixed)

Matches the concert decision; the A/B below used `medium` and it grounded correctly for both searchers. (flash-lite's prod default was `high` and still under-grounded.)

### D4: refresh the integration-test fixtures to current Vaundy data

The sales-phase fixture (HORO Feb–Mar 2026 presales) was stale/closed; refreshed to the `ぴあ抽選先行` phase (announced 2026-07-16, post-cutoff) so the test is a real grounding/freshness discriminator. The merch Vaundy case series was refreshed to the current tour; a goods-having artist (ヨルシカ) is the merch discriminator (Vaundy has no tour goods page).

## A/B evidence (local, dev key, thinking=medium, 2026-07-27)

| Searcher | `gemini-3.1-flash-lite` | `gemini-3.6-flash` |
|---|---|---|
| sales-phase (Vaundy `ぴあ抽選先行`) | 0 phases found (under-grounded) | 1/1 exact — apply/result/payment dates + pia URL correct |
| merch (ヨルシカ「一人称」) | hallucinated `.../category_id=3428` (fake) | correct `store.plusmember.jp/yorushika/` |

Both flash-lite failures are quality defects, not just cost. 3.6-flash grounded post-cutoff data with `tool_use=0` (metadata under-reports, as with concert).

## Risks / Trade-offs

- **Token cost up on 3.6-flash** (sales ~5k vs ~1.9k tokens) → but flash-lite's cheap tokens produce wrong/empty results; and the per-search-query fan-out (the dominant cost) is expected to drop. Net verified via post-deploy billing.
- **Fan-out not measurable pre-deploy** (metadata invisible) → verify via the billing SKU after rollout.
- **Small A/B sample** (one artist per searcher) → the failure/success contrast is stark and consistent with the concert result; monitor prod discovery after rollout.

## Migration Plan

1. Backend: change merch defaults + config test; commit the refreshed integration-test fixtures. `make check` green.
2. Release backend (next minor); merch inherits the new defaults.
3. cloud-provisioning: sales-phase-discovery configmap → extract `gemini-3.6-flash` + thinking `medium`; bump the job pin (auto pin-bump may cover it; verify).
4. Verify post-deploy: billing "search query gemini 3 paid" SKU drops; sales-phase/merch discovery output still fresh and correct.

Rollback: revert the merch defaults / sales-phase env; no data migration.
