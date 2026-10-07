## 1. Official-site link discovery (components/entity/concert/search, backend)

- [ ] 1.1 Add the guarded HTTP client for the top-page fetch (design D2): dial-time refusal of loopback/private/link-local/unspecified/multicast addresses, `Proxy: nil`, http(s) only, at most 3 redirects with a redirect to another registrable domain yielding no links, 5 s timeout, body read up to 2 MB and parsed, service User-Agent; verify unit tests against `httptest` servers for "Top page unavailable" (403 → no links, no error), "Private address refused" (dial to a private address is not attempted), "Redirect to another domain" (no links) and "Top page larger than 2 MB" (a link in the first 2 MB is returned), plus a non-HTML body yielding no links
- [ ] 1.2 Implement link selection with a `linkProfile` of keyword tiers and a cap (design D1, D3) using `golang.org/x/net/html` and `publicsuffix`, and define `concertSearchProfile` (tier 1 live/schedule/tour/concert/show, cap 8): same registrable domain as the official site, `lang`/`_normalbrowse_*` and fragments dropped, de-duplicated, tiers filled in order with page order inside a tier; verify unit tests for "Concert pages linked from the top page", "Link to another domain ignored" and "More than 8 concert links", plus a two-tier test profile showing tier-2 links never displace tier-1 links
- [ ] 1.3 Implement the www fallback (design D5) and verify a unit test for "www host without DNS" with a resolver stub where `www.` is NXDOMAIN and the apex serves the page
- [ ] 1.4 Add the linked pages to the grounded call's user prompt (design D4), leaving the prompt byte-identical when there are none, and wire the guarded fetch client through `NewConcertSearcher` and the job, consumer and server DI, separate from the genai and shared external clients; verify a request-capture unit test shows the link block when the top page has links and today's prompt when it has none, and `go build ./...` passes

## 2. Rejected-request retry (components/entity/concert/search, components/entity/sales-phase/search-sales-phases, backend)

- [ ] 2.1 In ConcertSearcher, re-send a 400 once with `ToolConfig` cleared as a second `executePass` when the tool-invocation report was on (design D6), summing `RetryCount` and logging `tool_report_dropped`; verify unit tests for "Invalid request recovered without the tool report" (2 requests, second without `toolConfig`, concerts returned) and "Invalid request rejected twice" (2 requests, InvalidArgument error), and that the existing "Recovered on retry", "All attempts transient", "Response without a candidate", "Too many tool calls" and "Caller deadline expires" tests still pass
- [ ] 2.2 In SalesPhaseSearcher, re-send a 400 once with `ToolConfig` cleared (design D6), logging `tool_report_dropped`; verify unit tests for "Invalid request recovered without the tool report" (2 requests, second without `toolConfig`, phases returned) and "Invalid request rejected twice" (2 requests, InvalidArgument), and that the existing "Spend cap reached", "No result" and "Service unreachable" tests still pass

## 3. URL context counts and link logging (backend)

- [ ] 3.1 Count `url_context_calls` and `url_context_succeeded`, and record `linked_pages` and `linked_page_urls`, per ConcertSearcher call into `PassMetadata` and the `successfully received Gemini response` log (design D7); verify a unit test feeding a recorded response with URL context tool-call/tool-response parts (one SUCCESS, one ERROR) asserts the logged counts and the linked URLs
- [ ] 3.2 Log `url_context_calls` and `url_context_succeeded` in SalesPhaseSearcher's `logResponseMetadata` (design D7); verify a unit test with the same recorded parts asserts the logged counts

## 4. Evaluation and release (backend)

- [ ] 4.1 Add the LINKS and LINKS+NEWS harness variants and record the D8 evaluation (fixture artists, 2 prod search-only artists, a site without extractable links, a non-Japanese site; ≥3 reps, `GEMINI_GROUNDING_EVAL_TOOL_CALLS=1`); verify LINKS meets the D8 pass criteria and the harness README records both variants' results
- [ ] 4.2 If LINKS+NEWS passes D8 and saves search queries against LINKS, add the news-index tier 2 to `concertSearchProfile` with a selection unit test, and update the spec requirement and design D3 in the store to name news indexes; otherwise record in the harness README why it was not adopted
- [ ] 4.3 Open the backend PR, get CI green including `make check`, merge and cut a release; verify the release tag exists and the automated `bump-prod-pin` moved the prod pin to it

## 5. Production check

- [ ] 5.1 After the first scheduled prod runs on the release, verify in the job logs that concert search calls for artists with links carry `linked_pages > 0` and `url_context_succeeded > 0`, that search queries per call dropped against the 2026-10-06 baseline (17.0 per searched artist), that go!go!vanillas no longer fails with INVALID_ARGUMENT, and that the sales phase discovery job logs `url_context_calls` / `url_context_succeeded` with no INVALID_ARGUMENT
