## Context

The concert search pipeline uses an async fire-and-forget pattern: the RPC returns immediately, a background goroutine calls Gemini, and the frontend polls `ListSearchStatuses` every 2 seconds with a 15-second per-artist timeout. When users follow many artists quickly, the Gemini calls queue up and most artists exceed the frontend timeout, causing the onboarding coach mark to never appear.

The backend already has a synchronous `SearchNewConcerts` usecase method used by the CronJob. The RPC handler wraps it in `AsyncSearchNewConcerts` (a goroutine). Removing this wrapper and returning concerts directly simplifies the entire pipeline.

## Goals / Non-Goals

**Goals:**
- Eliminate polling: frontend awaits SearchNewConcerts and gets concerts in the response
- Delete all polling infrastructure (backend + frontend, ~650 lines total)
- Fix Dockerfile log level override
- Keep the 24h search_log cache guard to avoid redundant Gemini calls

**Non-Goals:**
- Batching multiple artists into a single streaming RPC (unary per artist is sufficient)
- Changing the search_log table schema (just stop using `ListByArtistIDs`)
- Modifying the CronJob (already uses sync SearchNewConcerts)

## Decisions

### 1. Unary sync RPC, not server-side streaming

**Choice**: Keep `SearchNewConcerts` as unary RPC, make it synchronous (block until Gemini completes), return `repeated Concert concerts` in the response.

**Alternatives considered**:
- Server-side streaming for multiple artists → unnecessary complexity; frontend follows one artist at a time
- Keep async + increase timeout → band-aid; polling adds 6+ RPCs per artist

**Rationale**: The simplest possible change. One RPC call per artist, one response with concerts. No polling state machine.

### 2. 60-second context timeout

**Choice**: Apply `context.WithTimeout(ctx, 60*time.Second)` in the usecase layer's `SearchNewConcerts`. The RPC handler passes context through without additional timeout.

**Rationale**: Gemini calls take 8-15 seconds typically. 60 seconds provides ample buffer for retries (3 attempts with backoff). Gateway/LB timeouts should be >= 60s (verify).

### 3. Return discovered concerts, not persisted concerts

**Choice**: `SearchNewConcerts` returns the concerts it discovers and persists in this call. The response includes only newly discovered concerts (after deduplication), not all existing concerts for the artist.

**Rationale**: The frontend only needs to know "were concerts found?" for the coach mark. Returning discovered concerts avoids an extra `List` RPC.

### 4. SearchNewConcerts return type change

**Choice**: Change the Go usecase method signature from `error` to `([]*entity.Concert, error)`. The handler maps entity concerts to proto concerts for the response.

### 5. Delete ListSearchStatuses entirely

**Choice**: Remove the RPC, handler, usecase method, mapper, proto messages, and enum. No deprecation period.

**Rationale**: Only consumer is the frontend polling loop. Both sides deploy together in the same change. No external consumers.

### 6. Keep search_log for deduplication

**Choice**: Keep `SearchLogRepository` with `GetByArtistID`, `Upsert`, `UpdateStatus`, `Delete`. Remove only `ListByArtistIDs` (used exclusively by ListSearchStatuses).

**Rationale**: The 24h TTL cache guard prevents redundant Gemini API calls. Removing it would waste API quota.

### 7. Fix Dockerfile log level

**Choice**: Remove `ARG VITE_LOG_LEVEL` and `ENV VITE_LOG_LEVEL=${VITE_LOG_LEVEL}` from Dockerfile. The `.env` file's `VITE_LOG_LEVEL=debug` flows through `COPY . .` and Vite reads it automatically.

**Rationale**: The `ENV` line overrides `.env` with an empty string when CI doesn't pass `--build-arg`. Removing it is the simplest fix.

## Risks / Trade-offs

- **[Gateway timeout]** 60s RPC requires gateway/LB to allow long requests. Verify GKE Gateway timeout config (default is usually 30s) → may need to set `timeout` annotation on the HTTPRoute
- **[Breaking proto change]** Removing RPCs and messages is a breaking change. Since BSR consumers (backend + frontend) deploy together, coordinate via dependency order: specification PR → release → backend + frontend PRs
- **[UX during long search]** Frontend blocks on `await searchNewConcerts` for up to 60s per artist. The bubble absorption animation provides immediate feedback, but no progress indicator for the Gemini search. Consider adding a subtle loading state in a follow-up change
