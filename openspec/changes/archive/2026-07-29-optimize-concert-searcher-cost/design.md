## Context

`ConcertSearcher.Search` runs a two-step Gemini pipeline. Step 1 (grounded extract) currently fans out into three parallel slices (`tours_near`, `tours_far`, `standalones`) on `gemini-3.5-flash` with `{GoogleSearch, URLContext}` enabled. Production billing analysis (Cloud Billing Export ↔ Cloud Logging) established:

- The `google_search` tool performs invisible automatic query expansion: **~22x** metered "search query" units per request on `gemini-3.5-flash`, none surfaced in `groundingMetadata.webSearchQueries`. `flash-lite` features fan out only ~2x.
- Search-query charges are **~59–69%** of total Gemini spend (June ¥3,298; recurring in July after the cap reset and free-tier exhaustion).
- Concert discovery is **~97%** of search-query volume, because the fan-out (~22x) is multiplied by the 3-slice design.
- `google_search` cannot be removed: an artist's official top page does not enumerate all concerts, so live search is required for coverage.

Constraints: no proto/API change; prompts and code comments in English (repo global constraint); prod verification via the billing-export SKU (dev env is intentionally stopped).

## Goals / Non-Goals

**Goals:**

- Cut the Step 1 search-query fan-out and token cost while preserving discovery recall/precision.
- Move the extract step to `gemini-3.6-flash` (cheaper output, better efficiency/accuracy).
- Collapse the 3-slice fan-out to a single grounded call.
- Replace the tour/standalone split prompts with one consolidated, optimized English prompt.
- Decide the thinking level empirically via the existing A/B harness.

**Non-Goals:**

- No change to `SalesPhaseSearcher` or `MerchSearcher`.
- No change to Step 2 (parse) model or schema.
- Not removing `google_search` (required for coverage).
- Not resolving the platform-side billing/observability defect (tracked separately via Google support).

## Decisions

### D1: Extract model `gemini-3.5-flash` → `gemini-3.6-flash`

3.6-flash has lower output price ($9→$7.50 /1M), better token efficiency, and higher benchmark accuracy per the model card, at the same input price. It stays a flash-class model, so extraction quality should hold or improve. Alternative considered: `gemini-3.1-flash-lite` (as sales uses) — rejected for this change because the user prioritizes discovery quality; lite remains a possible future A/B arm.

Note: the per-query grounding price is a gemini-3 family SKU and is **model-independent**, so the model swap does NOT by itself reduce search-query cost — only the token portion. Whether 3.6-flash fans out less than 3.5-flash is unknown and is a primary A/B measurement.

### D2: Consolidate Step 1 to a single slice

`defaultStep1Slices` goes from three entries to one that extracts both tours and standalones over an open-ended window. This removes the 3x slice multiplier directly. Alternative: keep 3 slices but lite-ize — rejected (quality priority + still pays 3x). The fan-out mechanism (`sync.WaitGroup` slice loop) is retained so slice count stays configurable.

### D3: Open-ended (start-date-only) window

The prompt supplies a start date and no end date; the near/far range split is removed. Rationale: concert discovery wants all future concerts from "now" onward; a fixed far boundary added a slice without clear benefit. Drops the `to_date` placeholder from the template.

### D4: One consolidated English prompt with explicit coverage rules

A single `systemInstructionStep1` extracts `<tour>` and `<standalone>` in one envelope, instructs discovery via `url_context` + `google_search` including off-domain tour pages, and excludes multi-artist festivals (a 2–4 act named co-headliner bill stays a standalone). All extraction rules (verbatim copy, page-context year inference, `(local_date, venue, start_time)` dedup, XML-only output) are preserved. Prompts authored in English (Japanese draft agreed).

### D5: A/B over `thinking ∈ {low, medium}` before prod

Use `GEMINI_AB_EVAL=1` against the frozen ground-truth fixture. Fixed axes: model `gemini-3.6-flash`, 1 slice, `{GoogleSearch, URLContext}`. Variable: thinking. Metrics measurable per run: **recall/precision** vs ground truth and **token cost** (from `usageMetadata`). The search-query **fan-out is NOT reliably measurable per A/B run** — it never appears in the API response (`webSearchQueries` is empty) and the billing export is ~24h-lagged and hourly-bucketed, so it cannot be attributed to a short ad-hoc run. Fan-out reduction is therefore validated **post-deploy** via the billing-export SKU trend (see Migration Plan), not in the A/B. Ship the thinking setting that holds recall at the lowest token cost.

## Risks / Trade-offs

- **Recall drop from merging near/far + tour/standalone** → A/B recall gate against the frozen fixture; do not ship if recall regresses.
- **Fan-out rebound**: a single broader request may expand to more internal queries, partially offsetting the 3x slice saving. This cannot be measured in the A/B (fan-out is invisible in the response and billing is lagged/bucketed) → validate post-deploy via the billing SKU trend; if the SKU does not drop as expected, revisit slice/thinking config.
- **3.6-flash search behavior unknown** → measured in A/B; if fan-out stays ~22x, the token saving still lands and slice-consolidation (3x) still applies.
- **Entity misclassification (tour vs standalone) in the merged prompt** → A/B precision gate; keep explicit definitions in the instruction.
- **Prompt regression risk** (rewrite touches the highest-value path) → keep Step 2 and the dedup/parse logic unchanged; only Step 1 instruction/slice/model change.

## Migration Plan

1. Implement backend changes (config default, single slice, consolidated English prompt, drop `to_date`); keep old constants removable only after A/B.
2. Run the A/B matrix locally/in a bounded run; record recall/precision + cost per thinking level.
3. Choose the winning thinking level; set it and `GCP_GEMINI_SEARCH_MODEL_EXTRACT=gemini-3.6-flash` for the concert-discovery job.
4. Ship backend, then update the cloud-provisioning prod overlay (model + thinking env); re-tighten the spend cap as an interim guardrail.
5. Verify post-deploy: the "search query gemini 3 paid" SKU drops in the billing export and discovery recall holds in prod.

Rollback: revert `GCP_GEMINI_SEARCH_MODEL_EXTRACT` / thinking env and the `defaultStep1Slices` change; the pipeline shape (two-step, tools) is unchanged so rollback is config + code revert with no data migration.

## Resolved by A/B (2026-07-27, dev key, refreshed fixture: Vaundy + SUPER BEAVER)

- **Thinking level → `medium`.** `low` truncated Vaundy's long 2027-2028 tour (one run dropped 10 real 2028 dates); `medium` enumerated the full tour every run, with only 2 unmatchable "会場未定/TBD" placeholder misses (effectively perfect discovery). SUPER BEAVER: 0.99 (medium) vs 0.97 (low). Medium is required for long-tour completeness.
- **3.6-flash token efficiency confirmed**: extract-step thinking tokens 94–1,253 vs 3.5-flash's 4,000–5,500 per slice.
- **Fan-out remains unmeasurable in the A/B**: all cells returned `webSearchQueries=0` and the harness `total_cost=$0`, so the search-query fan-out (the dominant cost) cannot be observed per run — deferred to post-deploy billing verification (task 6.2). Open risk: `medium`'s deeper reasoning may increase the invisible fan-out vs `low`.

## Open Questions

- Does `gemini-3.6-flash` (with `medium` thinking) reduce the ~22x fan-out vs 3.5-flash, or only the token cost? Only answerable post-deploy via the billing SKU (task 6.2).
- The single open-ended window did not produce far-future speculative dates in the A/B (precision held); keep watching precision in prod.
