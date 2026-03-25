## Context

The concert search usecase (`concertUseCase` in `internal/usecase/concert_uc.go`) is one of the most complex usecases in the backend, handling external API calls (Gemini), deduplication, entity construction, and event publishing. Over time it has accumulated structural issues that hinder testability and violate Clean Architecture boundaries.

The parallel change `extract-entity-domain-logic` introduces `ScrapedConcert.ToConcert()` for entity construction, which this change depends on for item 1 (the defer pattern cleanup removes inline construction code that moves to the entity method).

## Goals / Non-Goals

**Goals:**
- `executeSearch` has a single `defer` block for search status marking, eliminating 5 scattered calls
- The concert usecase has zero direct imports from `internal/infrastructure/`
- Time-dependent tests use `testing/synctest` (Go 1.25+ standard library) for deterministic behavior without production code changes
- `resolveUserID` exists in exactly one location, shared by concert and follow usecases

**Non-Goals:**
- Changing any external behavior (RPC responses, event payloads, database writes)
- Refactoring the dedup logic itself (separate concern)
- Refactoring Gemini prompt construction or retry logic
- Introducing a custom Clock interface (Go 1.25 `testing/synctest` eliminates the need)

## Decisions

### 1. Defer pattern for markSearchFailed / markSearchCompleted

The `executeSearch` method is refactored to use named return values and a single `defer` block:

```go
func (uc *concertUseCase) executeSearch(ctx context.Context, artistID uuid.UUID) (_ []*entity.Concert, err error) {
    defer func() {
        if err != nil {
            uc.markSearchFailed(ctx, artistID)
        } else {
            uc.markSearchCompleted(ctx, artistID)
        }
    }()
    // clean sequential flow with early returns
}
```

This eliminates all 5 scattered `markSearchFailed` calls and the single `markSearchCompleted` call at the end. Each error path simply returns the error, and the defer handles status marking uniformly.

**Alternative considered:** Wrapping the entire method in a helper that calls markSearchFailed on error. Rejected because it adds indirection without benefit over the defer pattern.

### 2. Remove infrastructure/geo dependency via CentroidResolver interface

The `geo.ResolveCentroid` function is called in `ListWithProximity` to convert a `Home` entity into lat/lng coordinates. This is a Clean Architecture violation: the usecase layer directly depends on infrastructure.

**Chosen approach:** Define a `CentroidResolver` interface in the usecase layer:

```go
type CentroidResolver interface {
    ResolveCentroid(home *entity.Home) (lat, lng float64, err error)
}
```

The existing `infrastructure/geo` package implements this interface. The `concertUseCase` struct receives the resolver via dependency injection.

**Alternative considered:** Moving centroid resolution to `Home.ResolveCentroid()` on the entity. Rejected because centroid resolution involves geocoding logic (mapping admin areas to coordinates) that is inherently an infrastructure concern -- it would bloat the entity with data that belongs in a lookup table or external service.

### 3. Deterministic time via `testing/synctest` (no Clock interface)

**Research finding:** Go 1.25 (Aug 2025) graduated `testing/synctest` to stable. Inside a `synctest.Test(t, func(t *testing.T){...})` bubble, all `time.Now()`, `time.Sleep()`, `time.Since()`, and timer operations transparently use a **fake clock** that advances instantly when all goroutines are blocked.

**This eliminates the need for a custom `Clock` interface entirely.** Production code keeps calling `time.Now()` / `time.Since()` directly — zero instrumentation needed. Tests wrap their body in `synctest.Test` to control time deterministically.

This affects 3 call sites in concert_uc.go that previously required mocking:
- L207: `time.Since(searchLog.SearchTime)` for freshness check
- L214: `time.Since(searchLog.SearchTime)` for pending timeout
- L268: `time.Now()` passed to `concertSearcher.Search`

**Why not a Clock interface?** The `benbjohnson/clock` library is archived (May 2023). Custom Clock interfaces add a constructor parameter to every usecase that touches time, increasing test boilerplate. `synctest` achieves the same goal with zero production code changes, which is strictly better.

**Important:** `synctest` only helps tests. If a future production use case requires a swappable clock (e.g., rate limiter), a Clock interface can be introduced at that point. YAGNI for now.

### 4. resolveUserID consolidation

`resolveUserID` is duplicated in `concert_uc.go:185-191` and `follow_uc.go:87-93`, with `ListByFollowerGrouped` doing it inline as well. The function extracts a user ID from context claims.

**Chosen approach:** Move `resolveUserID` to a shared package-level function in `internal/usecase/` (e.g., `resolve.go` or `auth.go`). Both usecases call the shared function. This is a straightforward deduplication with no interface changes.

**Alternative considered:** Moving it to a middleware or interceptor. Rejected because the function is usecase-specific (it resolves a domain user ID from claims, not just authentication) and not all RPCs need it.

## Risks / Trade-offs

**[Risk] Dependency on extract-entity-domain-logic** -- The defer pattern cleanup in `executeSearch` removes inline entity construction code that is being replaced by `ScrapedConcert.ToConcert()` from the parallel change. If that change is not merged first, the defer refactoring must retain the inline construction temporarily. Mitigation: sequence the implementation so `extract-entity-domain-logic` merges first, or keep the inline code in an intermediate commit.

**[Constraint] `testing/synctest` is test-only** -- If a future production feature requires clock control (e.g., configurable TTL evaluation), a Clock interface would need to be introduced at that point. For now, `synctest` covers all testing needs without any production code changes.

**[Trade-off] CentroidResolver interface for a single call site** -- Introducing an interface for a function called in one place may seem over-engineered. However, it is the correct Clean Architecture boundary and enables testing `ListWithProximity` without an infrastructure dependency.
