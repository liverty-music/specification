## Context

See proposal.md for the motivation. Concert.Search is realized by the Gemini `ConcertSearcher` (backend `internal/infrastructure/gcp/gemini/searcher.go`). Since `tune-concert-search-grounding`, it makes one grounded call: Google Search + URL context, a JSON response schema, and `ToolConfig.IncludeServerSideToolInvocations=true`. The prompt carries only the artist name, the start date and the official-site URL. `NewConcertSearcher` already takes an `*http.Client`, which is the transport of the genai client.

SalesPhase.SearchSalesPhases is realized by the Gemini `SalesPhaseSearcher` (`sales_phase_searcher.go`). It sends the same tool-invocation report with URL context, but calls `generate` once with no retry loop, and logs only `url_context_retrieved`.

The backend #543 investigation (2026-10-07, dev key, 35 live calls) found two things:
- Without links, the model starts with `site:` searches, guesses tour URLs (`.../feature/tour2026`), fails to fetch them, and rebuilds dates from snippets.
- Listing the top page's concert links in the prompt (variant LINKS) brought search queries from 22.3 to 4.4 per call over 3 artists × 3 reps. Recall was unchanged, cost fell from $0.36 to $0.12, and latency was roughly halved. Every listed page was fetched with SUCCESS.

A sample of official top pages taken while planning (2026-10-07) was 1–63 KB of HTML, answered in 0.5–2.5 s, and linked news indexes and 6–10+ news articles next to the concert pages. Some tours live on their own domains (`ggv-asiatour2026.jp`, `clubgnu.com`).

The #542 investigation reproduced the go!go!vanillas 400 8/8 with the tool-invocation report on and 0/2 with it off. The error is emitted mid-stream, right after URL context fetches a malformed fan-club page.

The repo's only outbound-fetch guard is an allowlist (`fanarttv/logo_fetcher.go`). Official sites are arbitrary hosts from MusicBrainz, so an allowlist does not apply.

## Goals / Non-Goals

**Goals:**
- Make the URL-context mode the norm for artists whose official site links its concert pages.
- Build the link extraction once, so the sales phase search can adopt it with its own profile.
- Stop the 400 for artists whose pages break the Preview tool-invocation report, in both searchers.
- Count URL context use correctly in the logs of both searchers.

**Non-Goals:**
- Fetching page bodies in Go and passing their content. Rejected in #543: JS-rendered sites return empty bodies, many non-Japanese sites answer 403/429 to plain clients, and paged schedules would need site-specific parsing.
- Link discovery for SalesPhase.SearchSalesPhases. Its profile (ticket pages, news articles, tour pages) needs its own keyword design and evaluation; it is a follow-up change that reuses D1.
- Links to other registrable domains, such as tour-only domains or a fan club on its own domain. Allowing them would admit ticket vendors and social sites; a later change can revisit it with evidence from `linked_page_urls`.
- A switch to turn link discovery off. A rollback is a release revert (Migration Plan).
- A cap on search queries in the prompt (LINKS_CAP). It halved queries again in a small sample but is unverified for sites without links; it is left to a later evaluation.
- Correcting stored official-site URLs. The www fallback applies to the fetch only; the official-site refresh job owns the stored URL.
- Honoring robots.txt. The fetch is one GET of a public top page per artist per day, the same page a fan opens; an extra robots.txt request and parser are not worth it.

## Decisions

**D1. Shared link extraction with per-searcher profiles, inside the gemini package.**
- An unexported `officialPageLinks(ctx, siteURL, profile) []string` helper does the fetch (D2, D5) and the selection (D3). It is an input to one grounded call, not a domain operation, so it gets no entity interface.
- A `linkProfile` holds the path keywords as ordered tiers and the link cap. Profiles are named after the searcher entity and operation they serve: `concertSearchProfile` now, `salesPhaseSearchProfile` in the follow-up change.
- `concertSearchProfile`: tier 1 is `live`, `schedule`, `tour`, `concert`, `show`; the cap is 8. A tier 2 for news indexes is added only if the D8 LINKS+NEWS variant passes.
- The fetch has its own guarded `*http.Client`, passed to `NewConcertSearcher` as a second client next to the existing genai one, and built in the job, consumer and server DI. It is never the shared `extHTTPClient` of the consumer.
- Alternative considered: a new `Artist.ListConcertPages` entity operation. Rejected because no caller outside the searchers needs it, and the spec requirement already binds the observable behavior to Concert.Search.

**D2. Guarded fetch.**
- The HTTP client uses a `net.Dialer` whose `Control` hook rejects loopback, private (RFC 1918 / ULA), link-local, unspecified and multicast addresses. The check runs at dial time, so DNS rebinding and redirects are covered too.
- The transport sets `Proxy: nil`, so an environment proxy cannot move the dial to a proxy the guard would check instead of the site.
- Only `http` and `https` are allowed.
- At most 3 redirects, each re-dialled through the guard. A redirect to another registrable domain than the official site's ends the fetch with no links.
- 5 s total timeout per fetch.
- The body is read through `io.LimitReader` at 2 MB and the part read is parsed. A larger page is not an error: navigation links sit at the top of the page, and the planning sample was at most 63 KB.
- `Accept: text/html` and a `User-Agent` naming the service and a contact URL.
- Any error, a non-2xx status or a non-HTML content type yields no links. It is logged at Info, never an error.

Alternative considered: resolving the host first and checking the IP before the request. Rejected because it leaves a TOCTOU gap that a dial-time check does not.

**D3. Link selection.**
- Parse `<a href>` with `golang.org/x/net/html` (already in the module graph; it becomes a direct dependency).
- Resolve each href against the final response URL. Keep only `http(s)` links whose registrable domain equals the official site's, computed with `golang.org/x/net/publicsuffix.EffectiveTLDPlusOne` (so `member.vaundy.jp` counts for `vaundy.jp`). The official site's domain is taken from the stored URL before any redirect, or from the apex host after the D5 fallback, never from the redirect target.
- A link matches a tier when its path contains one of the tier's keywords, case-insensitively, as a path segment or a segment prefix (`/live/`, `/tour2026`, `/schedule/list`).
- Drop the fragment and the `lang` / `_normalbrowse_*` query parameters, de-duplicate, and keep page order.
- Fill the cap tier by tier: all tier-1 links in page order, then tier-2 links, and so on. A link matching several tiers counts in the first. This keeps a run of news articles from pushing the concert pages out.

**D4. Prompt.**
- When links exist, the user prompt gains a block after the official site: `Concert pages linked from the official site (read these with url_context):` followed by one URL per line. This is the evaluated LINKS form.
- The system instruction is unchanged.
- With no links the prompt is byte-identical to today's, so the fallback path keeps today's behavior.

**D5. www fallback.** If the fetch fails with a `*net.DNSError` whose `IsNotFound` is true and the host starts with `www.`, fetch the same URL with `www.` removed, once. Only the prompt's link block uses the fallback host; the `Official site:` line keeps the stored URL.

**D6. Rejected-request retry (#542).**
- Both searchers treat a `genai.APIError` with code 400 as follows when `IncludeServerSideToolInvocations` is set: the request is re-sent once with a copy of the config whose `ToolConfig` is cleared. A second 400 is permanent as today (`InvalidArgument`).
- ConcertSearcher: 400 is not retryable inside `executePass`, so the re-send is a second `executePass` call made by its caller with the reduced config, outside the 3-attempt transient budget. `PassMetadata.RetryCount` is the sum of both passes; every other count comes from the second pass, the one whose response is used.
- SalesPhaseSearcher: the re-send is a second `generate` call with the reduced config and its own `salesPhaseCallTimeout`.
- Both log `tool_report_dropped=true` on the call that used the reduced config, so the lost `search_queries` for that call are explained.

Alternative considered: turning the report off globally. Rejected because the report is the only source of search queries when groundingMetadata is absent (common on Gemini 3), and cost monitoring depends on it.

**D7. URL context counts.**
- While walking the parts, count `ToolCall` parts with `ToolType == URL_CONTEXT` as `url_context_calls`. Count `ToolResponse` parts for URL context whose per-URL status is `URL_RETRIEVAL_STATUS_SUCCESS` as `url_context_succeeded`. The exact field path is pinned by a recorded response in a unit test.
- Both searchers log the two counts. ConcertSearcher also puts them in `PassMetadata` and its `successfully received Gemini response` log; SalesPhaseSearcher puts them in `logResponseMetadata`.
- ConcertSearcher logs `linked_pages` (the number of links put in the prompt) and `linked_page_urls` (the links themselves) at Info. At most 8 URLs per call keep the log small, and the URLs are what a misselected link is diagnosed from.
- `url_context_retrieved` stays for comparison and is documented as excluding failed-only fetches.

**D8. Evaluation gate.** Before release, the harness gains two variants of the production prompt, LINKS (tier 1 only) and LINKS+NEWS (tier 1, then news indexes as tier 2). Both are run with `GEMINI_GROUNDING_EVAL_TOOL_CALLS=1`, at least 3 reps each, on:
- the 4 fixture artists;
- 2 artists that were search-only in prod (e.g. Novelbright, 夜の本気ダンス);
- 1 site without extractable links (e.g. YOASOBI);
- 1 non-Japanese site.

A variant passes when:
- the per-artist mean recall on the fixture artists is at least FINAL's;
- search queries per call fall for the artists with links;
- on the site without links, search queries per call stay within ±30% of FINAL's.

LINKS must pass for the release. LINKS+NEWS is adopted only if it passes and saves search queries against LINKS; then tier 2 is added to `concertSearchProfile`, and the spec requirement and D3 name news indexes before the PR.

## Risks / Trade-offs

- **[A malicious or compromised official site steers the fetch]** → The dial-time IP guard, scheme check, redirect cap with the domain check, size and time limits apply. Only URLs go to the model, never page content.
- **[Sites block plain clients (403/429) or render links with JS]** → Fall back to today's prompt. About 28% of the search-only Japanese sites in prod had no extractable links and are not improved.
- **[Tour pages on their own domains are not listed]** → The model still finds them through search as today. `linked_page_urls` and `linked_pages = 0` in prod show how often it happens, for the later change in Non-Goals.
- **[Linked pages include past tours or unrelated "show" pages (`/showroom`)]** → The model still filters by the start date and scope, and links are capped at 8. Evaluation recall guards this.
- **[One more HTTP request per Search; up to 5 s added on a slow site]** → This is small next to the 30–100 s grounded call. The fetch runs only for artists with an official site. The planning sample answered within 2.5 s.
- **[The rejected-request retry doubles cost for affected artists]** → It happens at most once per search, and only for a 400, which was 1 artist in 133.
- **[More URL context input tokens (59k vs 43k in evaluation)]** → This is outweighed by search-query savings: about $0.014 per query versus $0.75 per M input tokens.

## Migration Plan

1. Backend PR: shared link extraction and guard, concert prompt, 400 retry in both searchers, logging in both searchers, harness variants, unit tests, evaluation per D8. Then release.
2. The release reaches prod through the automated `bump-prod-pin`. No config change is needed.
3. After the first prod runs, check per concert search call `linked_pages`, `linked_page_urls`, `url_context_calls` / `url_context_succeeded` and `web_search_queries`, that go!go!vanillas succeeds, and that the sales phase discovery job logs the URL context counts and no INVALID_ARGUMENT.

Rollback: revert the backend release (pin to the previous tag). No data or config change is involved.
