## Why

In production, the `ConcertSearcher` Step 1 grounded call is the dominant driver of Gemini API cost. The `google_search` grounding tool performs invisible automatic query expansion (~22x metered "search query" charges per request on `gemini-3.5-flash`, none surfaced in `groundingMetadata.webSearchQueries`), and this expansion is amplified 3x by the three-slice fan-out. Grounding "search query" charges are ~59–69% of total Gemini spend (June ¥3,298, still accruing in July), and concert discovery accounts for ~97% of that search volume. We must cut this cost without degrading discovery recall/precision — `google_search` itself must stay (an artist's official top page does not list every concert).

## What Changes

- **Migrate the extract-step model** from `gemini-3.5-flash` to `gemini-3.6-flash` (output $9→$7.50 per 1M, better token efficiency and accuracy per the model card). Parse-step model is unchanged.
- **Consolidate Step 1 from three parallel slices** (`tours_near`, `tours_far`, `standalones`) **into a single slice** — one grounded call per artist instead of three. This directly removes the 3x slice multiplier on search-query fan-out and token usage.
- **Rewrite the Step 1 system instruction** into a single consolidated, optimized prompt that:
  - extracts both tours and standalones in one pass;
  - explicitly includes tour pages hosted on a **separate domain** from the official site;
  - excludes **music festivals with a multi-artist lineup** (a 2–4 act named co-headliner bill stays a standalone);
  - uses an **open-ended (start-date-only) window** — no end date.
  - Prompts are authored in **English** in the implementation (Japanese draft is agreed; convert to idiomatic English when implementing).
- **Keep `google_search` + `url_context`** on Step 1 (grounding is required for coverage).
- **A/B evaluate** the new configuration across `thinking ∈ {low, medium}` using the existing harness (`GEMINI_AB_EVAL=1`) against the frozen ground-truth fixture, measuring recall/precision and cost (search-query fan-out + tokens), then ship the winning setting to prod and verify the billing SKU drop.

Non-goals: `SalesPhaseSearcher` and `MerchSearcher` are unchanged in this change; no proto/API schema change.

## Capabilities

### New Capabilities

_None._ This change modifies existing searcher capabilities only.

### Modified Capabilities

- `gemini-searcher-config`: the default extract-step model constant changes from `gemini-3.5-flash` to `gemini-3.6-flash`.
- `gemini-grounded-extract-and-coerce`: Step 1 fans out into **one** slice instead of three; the consolidated slice extracts both tours and standalones via a single **English** instruction and a **three-placeholder** template; the Step 1 date window is open-ended (start-date only, no `to_date`); the extraction rules cover separate-domain tour pages and **multi-artist-festival exclusion**.

## Impact

- **backend** (`liverty-music/backend`):
  - `internal/infrastructure/gcp/gemini/searcher.go` — `defaultStep1Slices` (3→1), consolidated Step 1 system instruction + prompt template (drop `to_date` placeholder), slice date-offset logic.
  - `pkg/config` — `defaultSearchModelExtract` constant → `gemini-3.6-flash`.
  - A/B harness (`searcher_integration_test.go`) + `testdata/` — run the `{low, medium}` thinking matrix on the new config.
- **cloud-provisioning**: after A/B, set `GCP_GEMINI_SEARCH_MODEL_EXTRACT` / thinking env for the concert-discovery job in the prod overlay; re-tighten the spend cap as an interim guardrail.
- **Verification**: post-deploy, confirm the "search query gemini 3 paid" SKU drops in the billing export and discovery recall holds.
- No breaking API change; no BSR/proto change.
