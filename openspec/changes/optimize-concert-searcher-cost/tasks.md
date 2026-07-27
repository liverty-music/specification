## 1. Backend — config & model

- [x] 1.1 Change `defaultSearchModelExtract` in `pkg/config` from `gemini-3.5-flash` to `gemini-3.6-flash`; update the config unit test asserting the extract-step default.
- [x] 1.2 Confirm DI wiring (`internal/di/{provider,job}.go`) still threads `SearchModelExtract()` into `gemini.Config.ModelExtract` (no code change expected; verify).

## 2. Backend — single-slice consolidation

- [x] 2.1 Replace the three-entry `defaultStep1Slices` (`tours_near`, `tours_far`, `standalones`) with a single `all` slice (`FromMonthsOffset = 0`, no end offset).
- [x] 2.2 Drop the `to_date` placeholder from the Step 1 prompt template and remove the `to_date` computation in `runStep1Slice` (open-ended, start-date-only window).
- [x] 2.3 Update `assertStepInvariants` / any slice-count assumptions to accept a single slice; keep the `{GoogleSearch, URLContext}` tool invariant unchanged.

## 3. Backend — consolidated English prompt

- [x] 3.1 Merge `systemInstructionStep1Tour` + `systemInstructionStep1Standalone` into one `systemInstructionStep1` (English) that extracts both `<tour>` and `<standalone>` in one `<extracted>` envelope, preserving verbatim-copy / page-context year-inference / dedup / XML-only rules.
- [x] 3.2 Add the coverage rules to the prompt: discover via `url_context` + `google_search` including tour pages on a domain different from the official site; exclude music festivals with a multi-artist lineup (keep 2–4 act named co-headliner bills as standalones).
- [x] 3.3 Collapse the two prompt templates into one `promptTemplateStep1` (English): "extract tours and standalones on/after `<from_date>` for `<artist>`; exclude multi-artist festivals; official-site host: `<host>`".
- [x] 3.4 Verify Step 1 envelope parsing (`parseStep1Envelope`, `mergeAndDedupEnvelopes`) still handles a single merged envelope with both element types; adjust if the merge assumed multiple slices.
- [x] 3.5 Run `make check` (lint + unit tests) green.

## 4. A/B evaluation

- [x] 4.1 Update the A/B harness matrix (`searcher_integration_test.go`, `GEMINI_AB_EVAL=1`) to fix extract model=`gemini-3.6-flash` (parse fixed to `gemini-3.1-flash-lite`), 1 slice, `{GoogleSearch, URLContext}`, and vary `thinking ∈ {low, medium}`; Vaundy-only via `GEMINI_AB_EVAL_ARTISTS=Vaundy`.
- [x] 4.2 Ran the harness (dev Gemini key) against the refreshed fixture (Vaundy + SUPER BEAVER, eval_from 2026-07-27, 12 cells). Result: SUPER BEAVER recall≈0.97(low)/0.99(medium); Vaundy recall 0.77(low, unstable — one run 0.61)/0.89(medium, stable). All cells `webSearchQueries=0` (grounding stays invisible on 3.6-flash too).
- [x] 4.3 Captured per-run token cost. thinking tokens: 3.6-flash 94–1,253 (vs 3.5-flash 4,000–5,500) — much lower. Harness `total_cost=$0` and `webSearchQueries=0` confirm the search-query fan-out is NOT observable per run (verified post-deploy in 6.2).
- [x] 4.4 **Chosen: thinking=medium.** Failure analysis: with `low`, one Vaundy run truncated the long 2027-2028 tour (dropped 10 real 2028 dates); `medium` enumerated the full tour every run — its only misses were 2 unmatchable "会場未定/TBD" placeholder venues (fixture artifact), i.e. effectively perfect discovery. No recall regression: `medium` finds all matchable events. Caveat: medium's deeper reasoning may raise the (invisible) fan-out — confirm via billing in 6.2.

## 5. Prod rollout

- [ ] 5.1 Cut a backend release including the config/model/prompt changes (verify a dev AR image exists for the concert-discovery job image before release).
- [ ] 5.2 concert-discovery has NO `GCP_GEMINI_SEARCH_MODEL_EXTRACT` override, so it inherits the new `gemini-3.6-flash` default from the backend image (sales-phase-discovery explicitly overrides to flash-lite and is unaffected). In cloud-provisioning concert-discovery configmap.env: set `GCP_GEMINI_SEARCH_THINKING_EXTRACT=medium` (A/B-chosen value; confirm this is the effective thinking level vs the code default) and, for explicitness, optionally pin `GCP_GEMINI_SEARCH_MODEL_EXTRACT=gemini-3.6-flash`; bump the job image pin (auto pin-bump may omit discovery cronjobs — bump manually).
- [ ] 5.3 Re-tighten the Gemini spend cap as an interim guardrail; note who raised it and the new value.

## 6. Verification & close-out

- [ ] 6.1 Confirm ArgoCD syncs the prod overlay and the concert-discovery job runs the new image/config.
- [ ] 6.2 Verify in the billing export that the "Generate content search query gemini 3 paid" SKU drops on the next concert-discovery run (fan-out × 3-slice removed).
- [ ] 6.3 Verify discovery recall holds in prod (spot-check newly discovered concerts vs known announcements).
- [ ] 6.4 Update the Google support case with the deployed fix as evidence of remediation.
- [ ] 6.5 Verify the change (`/opsx:verify`) and archive it once all tasks are complete and shipped.
