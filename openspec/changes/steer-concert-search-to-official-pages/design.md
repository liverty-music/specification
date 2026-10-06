## Context

See proposal.md for the motivation. Concert.Search is realized by the Gemini `ConcertSearcher` (backend `internal/infrastructure/gcp/gemini/searcher.go`). Since `tune-concert-search-grounding`, it makes one grounded call: Google Search + URL context, a JSON response schema, and `ToolConfig.IncludeServerSideToolInvocations=true`. The prompt carries only the artist name, the start date and the official-site URL.

The backend #543 investigation (2026-10-07, dev key, 35 live calls) found two things:
- Without links, the model starts with `site:` searches, guesses tour URLs (`.../feature/tour2026`), fails to fetch them, and rebuilds dates from snippets.
- Listing the top page's concert links in the prompt (variant LINKS) brought search queries from 22.3 to 4.4 per call over 3 artists × 3 reps. Recall was unchanged, cost fell from $0.36 to $0.12, and latency was roughly halved. Every listed page was fetched with SUCCESS.

The #542 investigation reproduced the go!go!vanillas 400 8/8 with the tool-invocation report on and 0/2 with it off. The error is emitted mid-stream, right after URL context fetches a malformed fan-club page.

The repo's only outbound-fetch guard is an allowlist (`fanarttv/logo_fetcher.go`). Official sites are arbitrary hosts from MusicBrainz, so an allowlist does not apply.

## Goals / Non-Goals

**Goals:**
- Make the URL-context mode the norm for artists whose official site links its concert pages.
- Stop the daily 400 for artists whose pages break the Preview tool-invocation report.
- Count URL context use correctly in logs.

**Non-Goals:**
- Fetching page bodies in Go and passing their content. Rejected in #543: JS-rendered sites return empty bodies, many non-Japanese sites answer 403/429 to plain clients, and paged schedules would need site-specific parsing.
- A cap on search queries in the prompt (LINKS_CAP). It halved queries again in a small sample but is unverified for sites without links; it is left to a later evaluation.
- Correcting stored official-site URLs. The www fallback applies to the fetch only; the official-site refresh job owns the stored URL.

## Decisions

**D1. Link discovery lives inside the Gemini searcher.** Add an unexported `officialPageLinks(ctx, siteURL) []string` helper in the gemini package, with its own `*http.Client` passed to `NewConcertSearcher` (wired in the job, consumer and server DI alongside the Gemini client). It is an input to one grounded call, not a domain operation, so it gets no entity interface. Alternative considered: a new `Artist.ListConcertPages` entity operation. Rejected because no other caller needs it, and the spec requirement already binds the observable behavior to Concert.Search.

**D2. Guarded fetch.**
- The HTTP client uses a `net.Dialer` whose `Control` hook rejects loopback, private (RFC 1918 / ULA), link-local, unspecified and multicast addresses. The check runs at dial time, so DNS rebinding and redirects are covered too.
- Only `http` and `https` are allowed.
- At most 3 redirects, each re-dialled through the guard.
- 5 s total timeout per fetch; the body is read through `io.LimitReader` at 2 MB.
- `Accept: text/html` and a descriptive `User-Agent`.
- Any error, a non-2xx status or a non-HTML content type yields no links. It is logged at Info, never an error.

Alternative considered: resolving the host first and checking the IP before the request. Rejected because it leaves a TOCTOU gap that a dial-time check does not.

**D3. Link selection.**
- Parse `<a href>` with `golang.org/x/net/html` (already in the module graph; it becomes a direct dependency).
- Resolve each href against the final response URL. Keep only `http(s)` links whose host has the same registrable domain as the top page, computed with `golang.org/x/net/publicsuffix.EffectiveTLDPlusOne` (so `member.vaundy.jp` counts for `vaundy.jp`).
- Keep only links whose path contains one of `live`, `schedule`, `tour`, `concert` or `show`, case-insensitively, as a path segment or a segment prefix (`/live/`, `/tour2026`, `/schedule/list`).
- Drop the fragment and the `lang` / `_normalbrowse_*` query parameters, de-duplicate, keep page order, and stop at 8.

**D4. Prompt.**
- When links exist, the user prompt gains a block after the official site: `Concert pages linked from the official site (read these with url_context):` followed by one URL per line. This is the evaluated LINKS form.
- The system instruction is unchanged.
- With no links the prompt is byte-identical to today's, so the fallback path keeps today's behavior.

**D5. www fallback.** If the fetch fails with a `*net.DNSError` whose `IsNotFound` is true and the host starts with `www.`, fetch the same URL with `www.` removed, once. Only the prompt's link block uses the fallback host; the `Official site:` line keeps the stored URL.

**D6. Rejected-request retry (#542).**
- In `executePass`, a `genai.APIError` with code 400 on the grounded call while `IncludeServerSideToolInvocations` is set is not permanent on the first occurrence. The request is re-sent once with `ToolConfig` cleared, outside the 3-attempt transient budget.
- A second 400 is permanent as today (`InvalidArgument`).
- The log records `tool_report_dropped=true`, so the lost `search_queries` for that call are explained.

Alternative considered: turning the report off globally. Rejected because the report is the only source of search queries when groundingMetadata is absent (common on Gemini 3), and cost monitoring depends on it.

**D7. URL context counts.** While walking the parts, count `ToolCall` parts with `ToolType == URL_CONTEXT` as `url_context_calls`. Count `ToolResponse` parts for URL context whose per-URL status is `URL_RETRIEVAL_STATUS_SUCCESS` as `url_context_succeeded`; the exact field path is pinned by a recorded response in a unit test. `linked_pages` is the number of links put in the prompt. All three go into the `successfully received Gemini response` log and `PassMetadata`. `url_context_retrieved` stays for comparison and is documented as excluding failed-only fetches.

**D8. Evaluation gate.** Before release, the harness gains a variant for the production prompt with links and is run with `GEMINI_GROUNDING_EVAL_TOOL_CALLS=1`, at least 3 reps each, on:
- the 4 fixture artists, where recall must not drop;
- 2 artists that were search-only in prod (e.g. Novelbright, 夜の本気ダンス);
- 1 site without extractable links (e.g. YOASOBI), where queries must stay at today's level;
- 1 non-Japanese site.

## Risks / Trade-offs

- **[A malicious or compromised official site steers the fetch]** → The dial-time IP guard, scheme check, redirect cap, size and time limits apply. Only URLs go to the model, never page content.
- **[Sites block plain clients (403/429) or render links with JS]** → Fall back to today's prompt. About 28% of the search-only Japanese sites in prod had no extractable links and are not improved.
- **[Linked pages include past tours or unrelated "show" pages]** → The model still filters by the start date and scope, and links are capped at 8. Evaluation recall guards this.
- **[One more HTTP request per Search; up to 5 s added on a slow site]** → This is small next to the 30–100 s grounded call. The fetch runs only for artists with an official site.
- **[The rejected-request retry doubles cost for affected artists]** → It happens at most once per Search, and only for a 400, which was 1 artist in 133.
- **[More URL context input tokens (59k vs 43k in evaluation)]** → This is outweighed by search-query savings: about $0.014 per query versus $0.75 per M input tokens.

## Migration Plan

1. Backend PR: link discovery and guard, prompt, 400 retry, logging, harness variant, unit tests, evaluation per D8. Then release.
2. The release reaches prod through the automated `bump-prod-pin`. No config change is needed.
3. After the first prod run, check `linked_pages`, `url_context_calls` / `url_context_succeeded` and `web_search_queries` per call, and that go!go!vanillas succeeds.

Rollback: revert the backend release (pin to the previous tag). No data or config change is involved.
