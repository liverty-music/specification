## Context

See proposal.md - Why. Concert.Search is realized by the Gemini `ConcertSearcher` (backend `internal/infrastructure/gcp/gemini`), constructed in three workloads: the `concert-discovery` CronJob (`internal/di/job.go`), the `event-consumer` first-follow search (`internal/di/consumer.go`) and the API server (`internal/di/provider.go`). Today it makes two calls per Artist: Step 1 (gemini-3.6-flash, Google Search + URL context, XML envelope) and Step 2 (gemini-3.1-flash-lite, JSON schema, date/time/admin-area coercion).

Evaluation (2026-10-01..04, harness `TestConcertSearcher_GroundingVariants` on backend branch `test/refresh-vaundy-ab-fixture`, fixtures refreshed from official sites):

| configuration (gemini-3.8-flash, thinking low) | search queries / call | recall |
|---|---|---|
| current prompt, host only | 55 (Vaundy) | 0.94-1.00 |
| short prompt, full URL, 2-month window, temperature unset | Vaundy 39, UVERworld 14, SUPER BEAVER 16, BRADIO 10 | 0.87-1.00 |
| same, single-step JSON (final candidate) | 20-32 (high run-to-run variance, 6-70) | 0.86-1.00 after venue normalization |

Per-call search counts read from server-side tool invocations matched the billing export exactly (102 = 102, billing counts distinct queries per request). groundingMetadata is absent on Gemini 3 when search runs during thinking, so it cannot be used for this.

## Goals / Non-Goals

**Goals:**
- Ship the evaluated configuration as the default for every ConcertSearcher.
- Make empty responses visible and retried by the next daily run.
- Log every search query so cost can be monitored per call.

**Non-Goals:**
- sales-phase-discovery (its searcher, config and suspension are untouched).
- Fetching official pages in application code instead of URL context.
- Reworking the A/B harness beyond what the defaults require.

## Decisions

**D1. Model and generation settings.** Extract model `gemini-3.8-flash`, thinking `low`, temperature not sent. Unit prices of 3.6 and 3.8 flash are identical; the 3.8 migration guide says to strip temperature, and in evaluation temperature 0.3 increased searches on 3 of 4 artists. `medium` produced timeouts and empty responses. `Config.OmitTemperature` (already on the branch) is set for the concert searcher in all three DI sites; the shared `GCP_GEMINI_SEARCH_TEMPERATURE` stays for sales-phase.

**D2. Single grounded call returning JSON.** Step 1 sends `responseMimeType: application/json` with `singleStepResponseSchema` together with Google Search and URL context (structured output with built-in tools is supported on Gemini 3, Preview). The JSON is mapped onto the existing merge (past-date filter, repeat removal, series grouping) so the merge is unchanged. The XML envelope parsing, `systemInstructionStep2Parse`, the Step 2 call and the multi-slice fan-out are removed from the concert searcher; `ModelParse` is no longer required by `NewConcertSearcher`. Alternative kept XML + Step 2: equal accuracy in evaluation, but one more call and two parsers to maintain.

**D3. Prompt and schema split.** The system instruction states only scope, sources and the output contract:

```
You are a data-extraction agent for a live-music information system.

Extract the tours and shows of the given artist taking place on or after the given start date: tours, one-off shows, and co-headliner bills (対バン) organized by the artist. Exclude music festivals and cancelled shows. Return each tour or show as one series with one event per date.

Use only the artist's official site and official tour pages as sources. Do not use third-party sites. When a tour has a dedicated page, read that page with url_context and take every date of the tour from it. When a page is offered in several languages, read its default-language version (the URL without a language parameter such as ?lang=) and copy text in that language.

Respond with JSON that follows the response schema.
```

User prompt: `Extract the tours and shows of <artist> taking place on or after <YYYY-MM-DD>.\n\nOfficial site: <full official-site URL>`. Field formats and verbatim rules live only in the schema descriptions (venue/title verbatim incl. former-name annotations about the venue itself, excluding show titles/subtitles printed next to it; source_url = tour page, else concert detail page; admin_area = ISO 3166-2 first-level subdivision; local_date YYYY-MM-DD; open/start RFC3339 with the venue's UTC offset; series events `minItems 1`, see D10). The default-language rule was added after the 2026-10-05 live run: Vaundy's tour page offers `?lang=en/ko` versions and the model copied "Kitakyushu Messe" from one of them; the earlier prompt's "always extract the Japanese-language form" had been dropped. It is phrased as the site's default language rather than the artist's country because Artist carries no country. The same run showed show subtitles appended to venues (UVERworld 「日本武道館～PREMIUM LIVE on Xmas～」), so the venue description now limits annotations to the venue itself. Tool usage: reading the top page is not forced (that made the model read it every time but searches remained, because URL context does not follow links); instead a tour's dedicated page is to be read with url_context. Live runs on 2026-10-05 showed two modes: calls that used url_context issued 9-16 queries, calls that never did rebuilt dates from search snippets with 25-80 queries (one hit TOO_MANY_TOOL_CALLS) and misread dates and venues. With the vocabulary aligned to the series schema alone, 3 of 4 artists still fell into the search-only mode (140 queries in total); adding the tour-page rule made all 4 read their tour pages in that run (57 queries, recall unchanged or better), but the confirmation run with the same prompt fell back to the search-heavy mode on 2 of 4 (UVERworld 35 queries with no url_context, SUPER BEAVER 56; 133 in total) while keeping recall 1.00. The rule is kept because it costs nothing and helped in one run, but it does not reliably prevent the mode; the per-call `search_queries` log (D8) is how the mode is watched in production. Alternative of the "announced since" filter was dropped: it dropped dates added to existing tours.

**D4. Search window and full URL.** `GoogleSearch.TimeRangeFilter` starts 2 months before now, truncated to whole seconds (the API rejects sub-second precision). The official site is passed as a full URL (URL context requires the scheme); the host-only form is removed.

**D5. Admin area.** The schema asks for ISO 3166-2 codes; `geo.NormalizeAdminArea` passes any code matching `^[A-Za-z]{2}-[A-Za-z0-9]{1,3}$` through upper-cased and still maps Japanese prefecture names. This matches the Venue entity's admin area format, so overseas venues now keep their area.

**D6. Venue normalization.** `NormalizeVenue` (the repeat-removal key) applies NFKC, strips the Latin-1 middle dot and drops all whitespace, on top of the existing prefecture and punctuation stripping. It currently lives in `abeval_scoring.go` although production uses it; it moves to its own file in the gemini package. The entity-level listed-venue normalization used for StagedConcert matching is separate and unchanged.

**D7. Empty responses fail.** A response whose `candidates` is empty returns a new permanent error (`errNoCandidates`, wrapped with `backoff.Permanent`), logged with usage and prompt feedback. SearchNewConcerts already marks the SearchLog failed on error, so the next daily run searches the Artist again. No in-call retry: empty responses are billed (tens to hundreds of thousands of tool-use tokens) and, per the open report on gemini-3.6-flash (TOO_MANY_TOOL_CALLS / empty candidates with Google Search + URL context), a repeat of the same request is likely to fail the same way. Observed only with thinking `medium` or temperature 0.3; 0 of about 45 calls with the final configuration. Separately, a candidate's finish reason is checked before its text: a response that is not STOP often carries no text and was previously read as "no concerts" without a retry. TOO_MANY_TOOL_CALLS is not retried: it fails Search like an empty response (`errTooManyToolCalls`, `Unavailable`), so the SearchLog is marked failed and the next daily run searches again. In the first prod run after rollout, 5 attempts for 3 of 49 artists stopped this way after 40-68 queries each (263 of 890 queries, about 30%), and the retries fell into the same search-only mode before succeeding; deferring to the next day trades a one-day delay for those artists against that spend. Other non-STOP reasons (e.g. MAX_TOKENS) are still retried as incomplete responses and degrade to no results after 3 attempts.

**D8. Search query logging.** `tool_config.include_server_side_tool_invocations = true` on the grounded call (Preview, Gemini 3). Search queries come from the Google Search tool-call parts and fall back from groundingMetadata when it is absent. The `successfully received Gemini response` log carries `search_queries` (list) and `web_search_queries` (count), alongside the existing usage, finish and URL context fields, matching the sales-phase searcher's log.

**D9. Configuration and rollout.** Prod `concert-discovery` ConfigMap: `GCP_GEMINI_SEARCH_MODEL_EXTRACT=gemini-3.8-flash`, `GCP_GEMINI_SEARCH_THINKING_EXTRACT=low`, `GCP_GEMINI_SEARCH_CACHE_TTL=96h` (commit 2b19db0 on cloud-provisioning branch `chore/extend-concert-search-cache-ttl`). The code defaults become 3.8 flash / low so `event-consumer` and the API server follow without per-workload config. The prod suspend patch targets `(concert|sales-phase)-discovery-app`; its target narrows to `sales-phase-discovery-app`. The prod image pin is not a manual step: publishing the backend Release dispatches `bump-prod-pin`, which pushes the pin to cloud-provisioning `main` and ArgoCD rolls it out. The release therefore reaches `event-consumer` and the API server (which use the code defaults) as soon as it is published, while `concert-discovery` stays suspended until the ConfigMap and suspend PR merges.

**D10. One series list; type from venues.** The schema returns a single `series` list (title, source_url, events `minItems 1`) instead of `tours` and `standalones`. Go sets the SeriesType from the kept events: TOUR when they are at two or more venues by `NormalizeVenue` (venues not yet announced ignored), SINGLE otherwise, which is the SeriesType definition (TOUR multi-venue, SINGLE one venue, possibly several days). Nothing downstream branches on the type (the use cases only store and return it; the frontend does not read it), so the model no longer makes a judgment that only feeds a label. The 2026-10-05 live run had returned a two-day bill at one venue (UVERworld at LaLa arena TOKYO-BAY) as a tour. Trade-off: a tour first announced with one date is created SINGLE and keeps that type when later dates join the series; acceptable while no consumer reads the type. Separately announced shows sharing a title are kept apart by the schema description instead of by Go.

## Risks / Trade-offs

- [Preview features (structured output with tools, server-side tool invocations) change or are rejected] → `IncludeServerSideToolInvocations` stays a config switch; a 400 from the API is a permanent error visible in the job's failures, and the release can be rolled back by the prod image pin.
- [Empty responses now count as failures; the daily run stops after 3 consecutive failures] → acceptable: the stop is the intended alarm; frequency was 0 with the final configuration. Watch the `error` metric after rollout.
- [Search counts vary widely per call (6-70)] → per-call `search_queries` logging lets cost be watched in Cloud Logging; the AI Studio monthly spend cap remains the hard stop.
- ["organized by the artist" leaves out two-act bills hosted by another artist] → intended scope; such shows reach the catalog via that other artist's search when followed.
- [URL context content is billed as input tokens (up to ~480k tokens per call observed)] → still far cheaper than the search queries it replaces; visible in the logged usage.
- [Rate-limit / spend-cap 429 still degrades to "no results" and marks the SearchLog completed] → unchanged by this change; the spend cap is reset monthly. Called out for a follow-up.

## Migration Plan

1. Backend PR (from the evaluation branch, rebased): defaults, single-step JSON, empty-response error, logging, normalization, DI. CI green, merge, release.
2. cloud-provisioning PR: prod concert-discovery ConfigMap (model, thinking, TTL 96h), narrow the suspend patch to sales-phase, the prod image pin follows the release automatically (`bump-prod-pin`).
3. After ArgoCD sync, confirm `concert-discovery-app` is not suspended and `sales-phase-discovery-app` still is; check the first run's logs for `search_queries` and failures.

Rollback: revert the image pin and ConfigMap; re-suspend concert-discovery if needed.

## Open Questions

- Fixture admin areas for overseas venues are still "" (test-only); filling them with ISO codes can follow later.
