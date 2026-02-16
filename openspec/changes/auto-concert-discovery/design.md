## Context

The backend already has a fully functional `SearchNewConcerts` use case that discovers concerts via Gemini AI, deduplicates them, and persists new ones to the database. This is currently triggered only by user-initiated API requests. The `followed_artists` table tracks user-artist subscriptions, and Kustomize-based K8s manifests manage deployments.

The goal is to add a scheduled job that calls `SearchNewConcerts` for every followed artist daily, reusing the existing business logic with minimal new code.

## Goals / Non-Goals

**Goals:**
- Automate daily concert discovery for all followed artists
- Reuse existing `SearchNewConcerts` use case without modification to its core logic
- Keep the CronJob simple: sequential processing, fail-safe, exit 0
- Cost-optimize dev environment (weekly schedule)

**Non-Goals:**
- Parallel/concurrent processing of artists (MVP uses sequential loop)
- Notification delivery to users (separate future concern)
- Rate limiting or throttling of Gemini API calls
- New RPC endpoints or proto changes

## Decisions

### 1. Separate binary at `cmd/job/concert-discovery/main.go`

**Choice**: New binary with dedicated DI, not a flag on the existing API server.

**Rationale**: The API server carries HTTP server lifecycle, auth middleware, RPC handlers, in-memory caches, and background goroutines — none of which a one-shot batch job needs. A separate binary avoids starting and tearing down unnecessary infrastructure, keeps the Docker image small, and follows the existing `cmd/` convention (`cmd/api/`, `cmd/prototype-cli/`).

**Alternative considered**: `--mode=cronjob` flag on the API binary. Rejected because it would require conditional logic in DI and make the API binary's lifecycle more complex.

### 2. Lightweight DI via `InitializeJobApp` in `di/job.go`

**Choice**: A new `JobApp` struct with only the dependencies the CronJob needs (config, logger, DB, repos, Gemini searcher, ConcertUseCase). Separate from the server-oriented `App` struct.

**Rationale**: `InitializeApp` creates a `ConnectServer`, auth interceptors, RPC handlers, LastFM/MusicBrainz clients, and an in-memory cache with a background goroutine. The CronJob needs none of these. `JobApp` provides a clean shutdown path (`Closers` for DB and telemetry) without coupling to server lifecycle.

### 3. Circuit breaker: 3 consecutive errors stops the job

**Choice**: If `SearchNewConcerts` returns errors 3 times in a row, log a warning and stop processing further artists. Exit code remains 0.

**Rationale**: 3 consecutive failures likely indicate a systemic issue (Gemini API down, DB connection lost) rather than artist-specific problems. Continuing would waste resources and generate noise. Exiting with 0 prevents K8s from restarting the job (which would hit the same issue). A successful search resets the counter.

**Alternative considered**: Always continue regardless of errors. Rejected because it could produce hundreds of identical error logs when the root cause is systemic.

### 4. `ConcertRepository.Create` changes to variadic `...*Concert`

**Choice**: Change the `Create` method signature from `Create(ctx, *Concert)` to `Create(ctx, ...*Concert)` and implement as bulk INSERT.

**Rationale**: `SearchNewConcerts` currently creates concerts one-by-one in a loop. A variadic signature allows both single-insert (existing callers pass one argument) and bulk-insert (future optimization). The bulk INSERT reduces round-trips when discovering multiple concerts for an artist.

### 5. K8s schedule with Kustomize overlay

**Choice**: Base manifest defines daily 09:00 UTC (18:00 JST). Dev overlay patches to Fridays only (`0 9 * * 5`).

**Rationale**: Kustomize overlays already handle env-specific config for the API server. Using the same pattern for CronJob schedules keeps infrastructure consistent. Dev runs weekly to reduce Gemini API costs during development.

### 6. Existing 24h search cache respected

**Choice**: The CronJob does not bypass the `searchCacheTTL` guard in `SearchNewConcerts`.

**Rationale**: If a user manually searched an artist within the last 24 hours, the cache prevents redundant Gemini calls. Since the CronJob runs once daily, it naturally falls outside the 24h window for most artists. The rare case where a user searches at 17:59 and the job runs at 18:00 simply results in a skip — acceptable behavior.

## Risks / Trade-offs

- **Gemini API cost scales linearly with followed artists** → MVP has a small artist count. Monitor and add rate limiting if needed.
- **Sequential processing is slow for many artists** → Acceptable for MVP. Can add worker pool concurrency later.
- **No retry for individually failed artists** → The 24h cache will be cleared on failure (existing behavior), so the next day's run retries automatically.
- **CronJob image size** → Shares the same base image as the API server. Could optimize with a smaller image later but not worth the complexity for MVP.
