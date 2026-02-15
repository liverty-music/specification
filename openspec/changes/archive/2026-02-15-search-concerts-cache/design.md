## Context

`ConcertUseCase.SearchNewConcerts` currently calls the Gemini API on every invocation to scrape concert data. There is no mechanism to skip this call when the artist was recently searched. The frontend follow flow will trigger `SearchNewConcerts` when `List` returns empty, meaning multiple users following the same artist could each trigger a redundant Gemini call.

The backend follows a layered architecture: RPC handlers → UseCases → Repositories → External APIs. The concert repository already provides `ListByArtist` for DB reads. The change introduces a new `latest_search_logs` table and integrates it into the existing `SearchNewConcerts` flow.

## Goals / Non-Goals

**Goals:**
- Avoid redundant Gemini API calls when an artist was searched within 24 hours
- Introduce a `latest_search_logs` table to record search timestamps per artist
- Keep the existing `SearchNewConcerts` return contract (returns only newly discovered concerts)

**Non-Goals:**
- Periodic cron job for refreshing concert data (future work, uses the same `SearchNewConcerts`)
- Changing the `ConcertService.List` RPC behavior (remains a pure DB read)
- Frontend implementation details (handled in a separate change)

## Decisions

### 1. Search log granularity: per-artist (not per-user)

The search log tracks whether Gemini was called for a given artist, regardless of which user triggered it. This prevents duplicate Gemini calls when multiple users follow the same artist in quick succession.

**Alternative considered**: Per-user search log. Rejected because the Gemini search result is artist-specific and shared across all users. Per-user tracking would still allow redundant calls.

### 2. Cache window: 24 hours

A 24-hour TTL balances freshness with API cost. Concert announcements rarely change within hours, and a future cron job will handle periodic refresh independently.

**Alternative considered**: Configurable TTL via Pulumi config. Rejected as premature — 24 hours is a reasonable default and can be made configurable later if needed.

### 3. Return empty slice when cache hit (not DB results)

When a recent search log exists, `SearchNewConcerts` returns `[]` (empty). This preserves the semantic contract: "returns only newly discovered concerts." The frontend should call `List` first for existing data.

**Alternative considered**: Return DB results on cache hit. Rejected because it changes the method's semantics and duplicates `ListByArtist` behavior.

### 4. UPSERT pattern for search log

Use `INSERT ... ON CONFLICT (artist_id) DO UPDATE SET searched_at = NOW()` to handle both first-time and subsequent searches in a single query. This avoids race conditions from concurrent searches for the same artist.

### 5. Search log check placement: inside `SearchNewConcerts` usecase

The cache check lives in `ConcertUseCase.SearchNewConcerts`, not in the RPC handler. This keeps the caching logic within the business layer and ensures it applies regardless of the caller (RPC, cron job, etc.).

## Risks / Trade-offs

- **[Stale data for 24h]** → Acceptable. The cron job will refresh data periodically. Users can also manually trigger `SearchNewConcerts` from admin tools if needed.
- **[Race condition: concurrent first searches]** → Mitigated by UPSERT. Two concurrent calls may both call Gemini (since neither has a log yet), but the deduplication logic in `SearchNewConcerts` already handles duplicate concert records.
- **[Clock skew]** → Using database `NOW()` for both read and write ensures consistency. No application-side time comparison.
