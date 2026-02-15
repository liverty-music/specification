## Why

The `SearchNewConcerts` RPC calls the Gemini API on every invocation, even when the same artist was recently searched. After implementing the artist follow flow, the frontend will call `SearchNewConcerts` whenever `List` returns no concerts for a followed artist. Without caching, this leads to redundant Gemini API calls, increased latency, and unnecessary cost. A search log mechanism is needed to skip the external API call when a recent search has already been performed.

## What Changes

- Add a `latest_search_logs` table to track when each artist was last searched via Gemini.
- Modify `SearchNewConcerts` to check the search log before calling Gemini. If the artist was searched within the last 24 hours, skip the Gemini call and return an empty result.
- After a successful Gemini search, upsert the search log with the current timestamp.
- The frontend follow flow will call `ConcertService.List` first, then `ConcertService.SearchNewConcerts` only if no concerts are found.

## Capabilities

### New Capabilities
- `concert-search-log`: Tracks when each artist's concerts were last searched, enabling time-based caching of external API calls.

### Modified Capabilities
- `concert-search`: `SearchNewConcerts` gains a 24-hour cache check before calling the external search API. When a recent search log exists, it returns an empty list instead of calling Gemini.

## Impact

- **Database**: New `latest_search_logs` table (migration required).
- **Backend**: `ConcertUseCase.SearchNewConcerts` logic change, new repository methods for search log read/write.
- **Frontend**: Follow completion flow calls `List` then conditionally `SearchNewConcerts`.
- **Proto**: No changes required. Existing `List` and `SearchNewConcerts` RPCs are sufficient.
