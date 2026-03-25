## 1. executeSearch defer pattern

- [x] 1.1 Refactor `executeSearch` to use named return values `(_ []*entity.Concert, err error)`
- [x] 1.2 Add `defer` block that calls `markSearchFailed(ctx, artistID)` on `err != nil` and `markSearchCompleted(ctx, artistID)` on `err == nil`
- [x] 1.3 Remove all 5 scattered `markSearchFailed` calls and the `markSearchCompleted` call at the method end
- [x] 1.4 Replace inline `entity.Concert` construction with `ScrapedConcert.ToConcert()` (depends on `extract-entity-domain-logic` merge)
- [x] 1.5 Run `make check` and verify all existing tests pass

## 2. Remove infrastructure/geo dependency

- [x] 2.1 Define `CentroidResolver` interface in `internal/usecase/` (e.g., `resolver.go`)
- [x] 2.2 Implement `CentroidResolver` in `internal/infrastructure/geo/` wrapping the existing `ResolveCentroid` function
- [x] 2.3 Add `CentroidResolver` field to `concertUseCase` struct and inject via Wire
- [x] 2.4 Replace direct `geo.ResolveCentroid` call in `ListWithProximity` with the injected resolver
- [x] 2.5 Remove the `infrastructure/geo` import from `concert_uc.go`
- [x] 2.6 Run `make check` and verify `ListWithProximity` behavior is unchanged

## 3. Deterministic time tests with testing/synctest

- [x] 3.1 Update time-dependent concert search tests to use `synctest.Test(t, func(t *testing.T){...})`
- [x] 3.2 Add test: recently completed search is skipped (advance fake clock < searchCacheTTL)
- [x] 3.3 Add test: stale completed search triggers re-search (advance fake clock > searchCacheTTL)
- [x] 3.4 Add test: pending search within timeout is skipped (advance fake clock < pendingTimeout)
- [x] 3.5 Add test: stale pending search is retried (advance fake clock > pendingTimeout)
- [x] 3.6 Run `make check` and verify all tests pass deterministically

## 4. resolveUserID consolidation

- [x] 4.1 Create shared `resolveUserID` function in `internal/usecase/` (e.g., `resolve.go` or `auth.go`)
- [x] 4.2 Replace `resolveUserID` in `concert_uc.go:185-191` with a call to the shared function
- [x] 4.3 Replace `resolveUserID` in `follow_uc.go:87-93` with a call to the shared function
- [x] 4.4 Replace inline user ID resolution in `ListByFollowerGrouped` with a call to the shared function
- [x] 4.5 Delete the duplicated function bodies
- [x] 4.6 Run `make check` and verify all existing tests pass
