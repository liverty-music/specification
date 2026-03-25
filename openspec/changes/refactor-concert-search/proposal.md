## Why

The `executeSearch` method in `concertUseCase` (concert_uc.go:242-340) has accumulated several Clean Architecture violations and testability problems. `markSearchFailed` is called in 5 separate error-handling locations, making the control flow fragile and easy to break when adding new error paths. The usecase directly imports `infrastructure/geo`, violating the dependency rule. Direct `time.Now()` and `time.Since()` calls make timing-dependent logic non-deterministic in tests. Additionally, `resolveUserID` is duplicated across concert and follow usecases.

These issues increase the risk of regressions and make it harder to add comprehensive test coverage (tracked in `add-usecase-test-coverage`). This refactoring addresses the structural problems before adding tests.

## What Changes

- Replace 5 scattered `markSearchFailed` calls in `executeSearch` with a single `defer` block that checks the returned error
- Remove the direct `infrastructure/geo` import from the concert usecase by introducing an interface or moving logic to the entity layer
- Use `testing/synctest` (Go 1.25+ stdlib) for deterministic time in tests — no custom Clock interface needed
- Consolidate the duplicated `resolveUserID` helper into a shared location
- Adopt `ScrapedConcert.ToConcert()` for entity construction (introduced by the parallel `extract-entity-domain-logic` change)

## Capabilities

### New Capabilities

- `concert-search-internals`: Defines internal quality requirements for the concert search usecase -- architectural boundaries, testability constraints, and code structure rules. No external behavior changes.

### Modified Capabilities

- `concert-search`: No requirement changes. All existing behavior, dedup logic, and external interfaces remain identical. This refactoring is purely internal.

## Impact

- **backend**: Internal refactoring of `internal/usecase/concert_uc.go` and related files. No API, proto, or database changes.
- **specification**: No changes (no proto or external contract modifications).
- **frontend**: No changes (no API behavior changes).
- **cloud-provisioning**: No changes.
