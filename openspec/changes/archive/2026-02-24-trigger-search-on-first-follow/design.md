## Context

The `artistUseCase.Follow()` method currently persists the follow relationship and spawns a background goroutine to resolve the artist's official site. Concert discovery only happens via the frontend's onboarding `LoadingSequence` or the Kubernetes CronJob. This means artists followed outside onboarding have no concerts until the next CronJob cycle.

## Goals / Non-Goals

**Goals:**
- Trigger Gemini-based concert search immediately when an artist is followed for the first time (no prior search log).
- Reuse the existing `SearchNewConcerts` logic (24h cache, dedup, venue creation) without duplication.

**Non-Goals:**
- Changing the CronJob behavior or schedule.
- Making the search synchronous (blocking the Follow RPC response).
- Triggering search on every follow (only first-time per artist).

## Decisions

### 1. First-follow detection via `searchLogRepo.GetByArtistID`

**Decision**: Check `searchLogRepo.GetByArtistID(artistID)` — if `ErrNotFound`, it's a first follow.

**Alternatives considered**:
- Count followers via `ListFollowers`: Adds a DB query and race condition (concurrent follows).
- Track a boolean on the artist record: Requires schema change for minimal benefit.

**Rationale**: The search log already exists and is the source of truth for "has this artist been searched." No schema changes needed.

### 2. Inject `ConcertUseCase` into `artistUseCase`

**Decision**: Add `ConcertUseCase` as a dependency of `artistUseCase`.

**Rationale**: The dependency is unidirectional (`artistUseCase → ConcertUseCase`). `ConcertUseCase` depends on `artistRepo` (not `artistUseCase`), so no circular dependency.

### 3. Fire-and-forget goroutine

**Decision**: Run `SearchNewConcerts` in a background goroutine with `context.WithoutCancel`, same pattern as `resolveAndPersistOfficialSite`.

**Rationale**: The Follow RPC should return immediately. Search errors are logged and swallowed — they don't affect the follow operation.

### 4. Search runs independently of official site resolution

**Decision**: Don't wait for `resolveAndPersistOfficialSite` to complete before searching. `SearchNewConcerts` already handles `nil` official site gracefully.

**Rationale**: Waiting would add latency to the background task. The search works without an official site (slightly lower quality results), and the next CronJob cycle will re-search with the site available.

## Risks / Trade-offs

- **Race with CronJob**: CronJob may search the same artist concurrently → Mitigated by 24h search log cache; at worst a duplicate Gemini call occurs, and concert dedup prevents duplicate DB entries.
- **Gemini API cost**: Each first-follow triggers an API call → Acceptable; only fires once per artist (search log prevents repeats).
- **Background goroutine errors are silent**: Search failure won't be visible to the user → Same pattern as existing `resolveAndPersistOfficialSite`; errors are logged for observability.
