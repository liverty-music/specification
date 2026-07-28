## Why

After the concert-searcher migration to `gemini-3.6-flash` (`optimize-concert-searcher-cost`, backend v1.24.0), the remaining Gemini search-query cost is `sales-phase-discovery` + `merch-discovery`, both on `gemini-3.1-flash-lite` (~¥448/day "search query gemini 3 paid"). A local A/B (thinking=medium, refreshed Vaundy fixture) shows flash-lite is not just costly but **lower quality**:

- **sales-phase**: flash-lite returned **0 phases** for Vaundy's current `ぴあ抽選先行` (JAPAN ARENA TOUR 2027-2028, announced 2026-07-16 — after the model cutoff), i.e. it under-grounded and found nothing. `gemini-3.6-flash` returned it **exactly** (apply 07-16→08-02, lottery result 08-08, payment 08-11, correct pia URL) — grounding live post-cutoff data.
- **merch**: flash-lite **hallucinated a non-existent deep link** (`.../products/list.php?category_id=3428`); `gemini-3.6-flash` returned the **correct official store URL** (`store.plusmember.jp/yorushika/`).

Per the concert finding, `gemini-3.6-flash` also bills grounding as cheap tokens rather than per-search-query fan-out — so this is a quality **and** cost win.

## What Changes

- **merch-discovery**: default model `gemini-3.1-flash-lite` → `gemini-3.6-flash`; default thinking `high` → `medium`.
- **sales-phase-discovery**: switch the Step 1 extract model from the `gemini-3.1-flash-lite` env override to `gemini-3.6-flash` (inherit the `defaultSearchModelExtract`), and thinking extract `high` → `medium`. The Step 2 parse model stays `gemini-3.1-flash-lite` (cheap, mechanical).
- **Test fixtures**: refresh the sales-phase and merch integration-test ground truth to current Vaundy data (a post-cutoff sale phase as the grounding/freshness discriminator).
- **Verify** post-deploy: the "search query gemini 3 paid" billing SKU drops further and discovery quality holds/improves.

Non-goals: no change to `ConcertSearcher` (already on 3.6-flash) or the email parser (Vertex AI, no grounding). No proto/API change.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `gemini-searcher-config`: add the merch-searcher model and thinking default constants (`defaultMerchModel = "gemini-3.6-flash"`, `defaultMerchThinkingLevel = "medium"`). The sales-phase extract model is not a new spec field — it uses the existing `SearchModelExtract()` resolution, so migrating it is a prod-overlay env change only.

## Impact

- **backend** (`liverty-music/backend`):
  - `pkg/config` — `defaultMerchModel` → `gemini-3.6-flash`, `defaultMerchThinkingLevel` → `medium`; update the config test.
  - `internal/infrastructure/gcp/gemini/{sales_phase,merch}_searcher_integration_test.go` — refreshed fixtures (current Vaundy tour / sale phase / official store).
- **cloud-provisioning**: `sales-phase-discovery` configmap.env — set `GCP_GEMINI_SEARCH_MODEL_EXTRACT=gemini-3.6-flash` (or drop the flash-lite override to inherit the default) and `GCP_GEMINI_SEARCH_THINKING_EXTRACT=medium`; keep `GCP_GEMINI_SEARCH_MODEL_PARSE=gemini-3.1-flash-lite`. merch-discovery inherits the new backend defaults (no env override today).
- **Verification**: post-deploy billing (search-query SKU) + spot-check sales-phase/merch discovery output freshness.
- No breaking API change; no BSR/proto change.
