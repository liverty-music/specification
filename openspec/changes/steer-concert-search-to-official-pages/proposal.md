## Why

Concert search makes one grounded Gemini call per artist. About 44% of those calls for Japanese artists with an official site never read the official pages. The model guesses tour-page URLs that do not exist, its URL context fetches fail, and it rebuilds every date from search snippets. That costs 20–70 search queries per call, causes all TOO_MANY_TOOL_CALLS stops, and has misread dates and venues (backend #543).

Separately, one artist (go!go!vanillas) fails every day with `400 INVALID_ARGUMENT`. The cause is the Preview server-side tool-invocation report breaking after URL context fetches a malformed page (backend #542).

Telling the model which concert pages the official site links to cut search queries from 22.3 to 4.4 per call in evaluation, with no loss of recall.

## What Changes

- Before the grounded call, Search reads the artist's official top page once and collects the same-site links that point to live, schedule, tour, concert or show pages. Those links go into the prompt as the pages to read with URL context.
  - If the page cannot be fetched or has no such links, Search runs as today.
  - If an official site's `www.` host does not resolve, the fetch retries on the apex host.
- When the grounded call is rejected as an invalid request, Search retries it once without the server-side tool-invocation report. A rejection of that retry fails Search as today.
- Each Gemini response log records the number of URL context calls, how many of them succeeded, and whether links were provided. Fetches that only failed no longer disappear from the count.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `components/entity/concert/search`:
  - New requirement: Search reads the concert pages linked from the artist's official site.
  - "Transient failures degrade to no results" gains the single reduced retry for a rejected request.

`components/usecase/concert/search-new-concerts` is unchanged. A rejected request that fails after its reduced retry is still a Search error, which marks the SearchLog failed as today. `components/entity/artist` is unchanged: the official site's stored URL is not rewritten; the apex fallback applies only to the fetch.

## Impact

- **backend:**
  - `internal/infrastructure/gcp/gemini`: request building, link extraction, retry on 400, response logging.
  - A guarded HTTP fetch of the official top page: timeout, size cap, refusal of private and loopback addresses, and same-site links only.
  - DI wiring of its HTTP client in the job, consumer and server.
- **Cost and latency:** one extra HTTP GET per Search, plus more URL context input tokens. These are far outweighed by the search queries saved (evaluation: $0.36 → $0.12 per call, latency roughly halved).
- **No proto, DB or cloud-provisioning change.**
