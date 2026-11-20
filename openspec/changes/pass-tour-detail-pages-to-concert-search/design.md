## Context

See proposal.md - Why. Concert.Search is the backend `ConcertSearcher` (`internal/infrastructure/gcp/gemini`): it reads the official top page (`officialPageLinks`, `concertSearchProfile`: concert keywords, then `news`, at most 8 links), lists those links in the prompt, and makes one grounded call to the Gemini API direct backend with Google Search (2-month `TimeRangeFilter`) and URL context, returning JSON. Prod runs `gemini-3.8-flash`, thinking `low`, temperature unset (prod overlay `concert-discovery/configmap.env`).

Constraints from the Gemini API docs (read 2026-11-20):

- URL context reads only the URLs in the request, "not any content from nested links", and at most 20 URLs per request.
- Google Search grounding on Gemini 3 and newer bills each search query: 5,000 free per month shared across all Gemini 3+ models, then $14 per 1,000, and at most 1,500 per day per project.
- `gemini-4-hydrogen` (stable) supports Google Search, URL context, structured output and thinking `low`/`medium`/`high`/`xhigh`; its standard price equals `gemini-3.8-flash`'s from 2027-01-01.
- No request parameter caps the number of search queries of a built-in tool; only the prompt can.

Prod evidence (PostHog `$ai_generation`, 2026-10-21..11-20): the calls with more than 40 queries returned 14.8 events on average and those with 1-5 queries 2.3, so the many-query artists are the long tours. The A/B fixture (`testdata/ab_ground_truth.json`, 4 artists, `evaluation_from` 2026-10-01) has no artist from that tail, and its events are now partly past.

## Goals / Non-Goals

**Goals:**
- Give the model the tour detail pages so it reads them instead of searching for them.
- Decide the model, thinking level and prompt of the grounded call on measured recall, queries and cost, before the 2027-01-01 price change.

**Non-Goals:**
- Shipping URL-context-only calls (no Google Search tool). It is evaluated here; shipping it changes Search's spec and is a follow-up change.
- Crawling deeper than one level below the top page, or reading JavaScript-rendered links.
- The sales phase searcher, #864 and #865 (proposal.md).

## Decisions

**D1. Read the concert pages and take their page-specific links.** After `officialPageLinks` selects the top page's links, the searcher fetches the first 3 links of the concert tier (not `news`) with the same guarded client (`NewOfficialPageClient`: 5 s, 2 MB, public addresses only, same registrable domain after redirects), concurrently. From each page it takes every same-domain `<a href>` (normalized as `matchLink` does, without the keyword filter) that is not the top page and not a link of the top page, de-duplicated, in page order, concert page by concert page. These go after the top-page links; the list stops at 20 (URL context's per-request limit).
  - Excluding the top page's links drops the site navigation (goods, profile, news index) that every page repeats, which leaves the page's own content: tour detail pages, ticket pages, articles. The keyword filter is not reused for this level: detail pages often have opaque paths (`/contents/123`), which a keyword rule would drop.
  - Alternative: keep only links under the concert page's path (`/live/` → `/live/tour-a/`). Rejected: sites in the prod tail put details elsewhere (`/contents/schedule` lists `/contents/<id>`).
  - Alternative: follow news pages too. Rejected: a news index links dozens of articles and would fill the 20 slots with unrelated pages.
  - 3 concert pages bound the extra fetches to 3 per Search; sampled top pages answered in under 2.5 s, and the fetches run in parallel.

**D2. The prompt lists the detail links in the existing block.** `linkedPagesHeader` keeps its wording ("Concert pages linked from the official site (read these with url_context)"); the detail links are appended to the same list. The generation report's `linked_page_urls` therefore carries them without a new field.

**D3. Evaluation design.** The A/B harness (`TestConcertSearcher_ABEval` for scored runs, `TestConcertSearcher_GroundingVariants` for unscored query counts) gets:
  - a refreshed fixture: the 4 current artists re-captured from official pages, plus at least 3 artists whose prod searches used more than 30 queries (fixture data comes from public official pages only);
  - switches for the variants: detail links on/off, model, thinking level, a search-cap prompt line ("Run at most 10 Google Search queries; read the listed pages with url_context first."), and Google Search tool on/off;
  - 3 repetitions per cell (run-to-run variance was 6-70 queries per call in the earlier evaluation), with tool-call query counting on (`GEMINI_GROUNDING_EVAL_TOOL_CALLS=1`), recording recall, queries per call, input/output tokens, cost at the post-2027 price, latency, empty responses and whether `groundingChunks` is present (backend #772).

  Runs, in order (each later run builds on the winner of the earlier ones):
  1. baseline (prod) vs detail links, on `gemini-3.8-flash`;
  2. the winner of 1 on `gemini-4-hydrogen` (thinking `low`);
  3. on the winning model: + search cap; thinking `minimal` (3.8 Flash) or the lowest level the model accepts; Google Search off for artists with detail links.

**D4. Acceptance criteria.** A variant is adopted when, against the configuration it replaces, over all fixture artists:
  - recall of public events is not lower by more than 0.02 (one event in 50);
  - median search queries per call on the many-query artists falls, and total cost per call does not rise;
  - no new empty responses, `TOO_MANY_TOOL_CALLS` stops or timeouts (120 s) appear.
  The model switch additionally needs p90 latency under 90 s. Results and the decision go into `docs/gemini-concert-searcher-tuning.md`. Google Search off is only reported (Non-Goals).

**D5. Shipping adopted settings.** A new model or thinking level changes `defaultConcertSearchModel` / `defaultConcertSearchThinking` in `pkg/config` and the prod pin in cloud-provisioning's prod overlay together, so the job, the event consumer and the API server (which use the code defaults) stay on one model. A search cap changes `systemInstruction`. The base `concert-discovery/configmap.env` drops its stale `gemini-3.6-flash` / `medium` lines and the comment that describes the removed two-step pipeline; the base keeps no model pin, as the event consumer and server bases do not.

**D6. Prod check.** After the release reaches prod, a week of `$ai_generation` (process `liverty-music-concert-discovery`) is compared with 2026-10-21..11-20: queries per call (mean, p90), share of queries from calls over 20 queries, events per call, and errors. This is a read-only check, not a dev run (dev is stopped).

## Risks / Trade-offs

- [More URL context input tokens per call; up to 20 pages instead of 8] → D4 rejects the change if cost per call rises; the 20-page cap bounds it.
- [Page-specific links include non-concert pages (ticket FAQ, articles)] → They cost tokens but do not change results: the prompt still asks only for the artist's shows; the evaluation measures recall and cost with them in.
- [JavaScript-rendered concert pages carry no links in their HTML] → Those artists keep today's behavior (searching); the prod check shows how many remain in the over-20 group.
- [Small fixture; a variant can win by chance] → 3 repetitions, and the prod check after release; a regression in prod reverts by config (model, thinking) or by a code revert (links).
- [`gemini-4-hydrogen` may behave differently with structured output plus built-in tools] → Covered by run 2's empty-response and invalid-JSON counts before any switch.
