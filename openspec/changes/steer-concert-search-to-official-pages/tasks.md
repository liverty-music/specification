## 1. Official-site link discovery (components/entity/concert/search, backend)

- [ ] 1.1 Add the guarded HTTP client for the top-page fetch (design D2): dial-time refusal of loopback/private/link-local/unspecified/multicast addresses, http(s) only, at most 3 redirects, 5 s timeout, 2 MB body cap; verify unit tests against `httptest` servers for "Top page unavailable" (403 → no links, no error) and "Private address refused" (dial to a private address is not attempted), plus oversized and non-HTML bodies yielding no links
- [ ] 1.2 Implement link selection (design D3) with `golang.org/x/net/html` and `publicsuffix`: same registrable domain, path naming live/schedule/tour/concert/show, `lang`/`_normalbrowse_*` and fragments dropped, de-duplicated, page order, at most 8; verify unit tests for "Concert pages linked from the top page", "Link to another domain ignored" and "More than 8 concert links"
- [ ] 1.3 Implement the www fallback (design D5) and verify a unit test for "www host without DNS" with a resolver stub where `www.` is NXDOMAIN and the apex serves the page
- [ ] 1.4 Add the linked pages to the grounded call's user prompt (design D4), leaving the prompt byte-identical when there are none, and wire the fetch client through `NewConcertSearcher` and the job, consumer and server DI; verify a request-capture unit test shows the link block when the top page has links and today's prompt when it has none, and `go build ./...` passes

## 2. Rejected-request retry and URL context counts (components/entity/concert/search, backend)

- [ ] 2.1 Retry a 400 from the grounded call once with `ToolConfig` cleared when the tool-invocation report was on (design D6), logging `tool_report_dropped`; verify unit tests for "Invalid request recovered without the tool report" (2 requests, second without `toolConfig`, concerts returned) and "Invalid request rejected twice" (2 requests, InvalidArgument error), and that the existing "Recovered on retry", "All attempts transient", "Response without a candidate", "Too many tool calls" and "Caller deadline expires" tests still pass
- [ ] 2.2 Count `url_context_calls`, `url_context_succeeded` and `linked_pages` per call into `PassMetadata` and the `successfully received Gemini response` log (design D7); verify a unit test feeding a recorded response with URL context tool-call/tool-response parts (one SUCCESS, one ERROR) asserts the logged counts

## 3. Evaluation and release (backend)

- [ ] 3.1 Add a harness variant for the production prompt with links and record the D8 evaluation (fixture artists, 2 prod search-only artists, a site without extractable links, a non-Japanese site; ≥3 reps, `GEMINI_GROUNDING_EVAL_TOOL_CALLS=1`); verify fixture recall does not drop versus FINAL, search queries per call fall for the linked sites, and the harness README records the results
- [ ] 3.2 Open the backend PR, get CI green including `make check`, merge and cut a release; verify the release tag exists and the automated `bump-prod-pin` moved the prod pin to it

## 4. Production check

- [ ] 4.1 After the first scheduled prod run on the release, verify in the job logs that calls for artists with links carry `linked_pages > 0` and `url_context_succeeded > 0`, that search queries per call dropped against the 2026-10-06 baseline (17.0 per searched artist), and that go!go!vanillas no longer fails with INVALID_ARGUMENT
