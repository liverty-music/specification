## Why

Concert search spends half of its Google Search queries on a few calls that hunt for tour detail pages. In prod over 2026-10-21..11-20, calls with more than 20 queries were 13% of the 549 concert searches but used 48% of their 5,208 queries, issuing `site:<official domain> "<tour name>"` / `"<date>"` one at a time. URL context reads only the URLs it is given, never the pages they link to (Gemini API docs, URL context "Best practices"), so the tour detail pages behind a live list page are found by searching. The searches went past the 5,000-per-month free tier by 738 queries (¥1,628, about half of the Gemini cost).

The model is due for a decision too: `gemini-3.8-flash` is previous-generation and its price doubles on 2027-01-01 to that of `gemini-4-hydrogen`. A Google Cloud customer engineer review (2026-11-20) also suggested capping searches in the prompt and lowering thinking; those need the same evaluation.

## What Changes

- The A/B harness is refreshed and extended with artists whose searches use many queries in prod, and evaluates, against `gemini-3.8-flash` with thinking `low`: reading the selected concert pages for their links (the tour detail pages), `gemini-4-hydrogen`, a prompt instruction capping the searches at 10, thinking `minimal`, and leaving the Google Search tool out. Every variant ships only when it meets the acceptance criteria in design.md (D4).
- Outcome of that evaluation: concert search moves to `gemini-4-hydrogen` (thinking `low`); the detail-page links, the search cap and thinking `minimal` are rejected, and Google Search stays.
- Per-artist results on `gemini-4-hydrogen` then showed it dropping shows the listed pages did not reach. Search now lists the official top page's links with their labels (link text or image alt text), links to other domains included, except well-known third-party domains and the site's own information pages, and the model picks the show pages (design D7). The prompt is rewritten for `gemini-4-hydrogen` with a purpose and a completion criterion (design D8).
- cloud-provisioning: the base `concert-discovery` ConfigMap's stale model and thinking values (`gemini-3.6-flash` / `medium`, overridden in prod) are removed, and the prod pin follows the adopted model.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `components/entity/concert/search`: "Search reads the official site's concert pages" is replaced by "Search lists the official top page's links": the top page's links of any domain, with their labels, go into the request except blocked domains and the site's own information pages, and the model picks the show pages (design D7). The first plan, also reading the selected concert pages for their links, was rejected in evaluation run 1 (search queries and cost rose) and removed.

`components/usecase/concert/search-new-concerts` is unchanged: it calls Search the same way and records the same outcomes. `components/entity/sales-phase/search-sales-phases` is unchanged: its searcher keeps its own model and settings, and moving it off `gemini-3.8-flash` before the 2027-01-01 price change is a separate decision. "Each external call reports its usage" is unchanged; the pages listed in the request already include every page this change adds.

## Impact

- **backend:** `internal/infrastructure/gcp/gemini` (official page link discovery, request building, prompt), the A/B harness and its fixture (`testdata/ab_ground_truth.json`), `pkg/config` defaults when another model or thinking level is adopted, and `docs/gemini-concert-searcher-tuning.md` for the results.
- **cloud-provisioning:** `k8s/namespaces/backend/base/cronjob/concert-discovery/configmap.env` and, if the model changes, the prod overlay pin.
- **Cost and latency:** the official top page is still read once per Search; the prompt grows by up to 60 labeled links (about 700–1,850 input tokens on the fixture), against the search queries and URL context reads it saves ($0.075 per call against $0.113 on the fixture, design D7). Goal: concert-discovery below about 4,000 queries a month, so every Gemini job fits the 5,000-query monthly free tier.
- **Out of scope:** spreading searches over days to stay under the 1,500-per-day search cap (backend #864), and registering official sites for the 27 artists that have none (backend #865).
- No proto or DB change.
