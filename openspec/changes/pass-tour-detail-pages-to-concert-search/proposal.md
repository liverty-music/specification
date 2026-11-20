## Why

Concert search spends half of its Google Search queries on a few calls that hunt for tour detail pages. In prod over 2026-10-21..11-20, calls with more than 20 queries were 13% of the 549 concert searches but used 48% of their 5,208 queries; their queries are `site:<official domain> "<tour name>"` and `site:<official domain> "<date>"`, issued one tour and one date at a time. Search already passes the concert pages the official top page links to, but URL context reads only the URLs it is given and never the pages they link to (Gemini API docs, URL context "Best practices"), so the tour detail pages behind a live list page are found by searching. The searches went past the 5,000-per-month free tier by 738 queries (¥1,628, about half of the Gemini cost).

The model is due for a decision too: `gemini-3.8-flash` is now listed as previous-generation, and its price doubles on 2027-01-01 to that of `gemini-4-hydrogen` ($1.50 / $7.50 per 1M tokens). A Google Cloud customer engineer review (2026-11-20) also suggested capping searches in the prompt and lowering thinking; those need the same evaluation before they ship.

## What Changes

- Search also reads the concert pages it selected from the official top page, and lists the official site's pages those concert pages link to (the tour detail pages) among the pages the model reads, so the model reads them with URL context instead of finding them by search. The same fetch limits apply as for the top page, and a page that cannot be read does not fail Search.
- The A/B harness is refreshed and extended with artists whose searches use many queries in prod, and evaluates, against `gemini-3.8-flash` with thinking `low`:
  - the detail-page links above;
  - `gemini-4-hydrogen`;
  - a prompt instruction that caps the searches at 10;
  - thinking `minimal`;
  - leaving the Google Search tool out when detail pages are listed (URL context only).
- Every evaluated variant ships only when it meets the acceptance criteria in design.md (D4), the detail-page links included: if they fail, they are removed from the implementation branch before it merges and this change drops its delta spec. The evaluated model, thinking level and prompt are adopted the same way. Leaving out the Google Search tool changes what Search searches, so if it qualifies it ships in a follow-up change with its own spec delta.
- cloud-provisioning: the base `concert-discovery` ConfigMap's stale model and thinking values (`gemini-3.6-flash` / `medium`, overridden in prod) are corrected, and the prod pin follows the adopted model.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `components/entity/concert/search`: "Search reads the official site's concert pages" also reads the selected concert pages and lists the official-site pages they link to.

`components/usecase/concert/search-new-concerts` is unchanged: it calls Search the same way and records the same outcomes. `components/entity/sales-phase/search-sales-phases` is unchanged: its searcher keeps its own model and settings, and moving it off `gemini-3.8-flash` before the 2027-01-01 price change is a separate decision. "Each external call reports its usage" is unchanged; the pages listed in the request already include every page this change adds.

## Impact

- **backend:** `internal/infrastructure/gcp/gemini` (official page link discovery, request building, prompt), the A/B harness and its fixture (`testdata/ab_ground_truth.json`), `pkg/config` defaults when another model or thinking level is adopted, and `docs/gemini-concert-searcher-tuning.md` for the results.
- **cloud-provisioning:** `k8s/namespaces/backend/base/cronjob/concert-discovery/configmap.env` and, if the model changes, the prod overlay pin.
- **Cost and latency:** up to 3 more HTTP GETs per Search to official pages, and more URL context input tokens; the evaluation weighs them against the search queries saved. Goal: concert-discovery below about 4,000 queries a month, so every Gemini job fits the 5,000-query monthly free tier.
- **Out of scope:** spreading searches over days to stay under the 1,500-per-day search cap (backend #864), and registering official sites for the 27 artists that have none (backend #865).
- No proto or DB change.
