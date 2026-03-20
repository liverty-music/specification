## Context

The backend has 80 test files across Clean Architecture layers. Tests were written incrementally as features shipped, resulting in style drift between layers. The go-tester skill defines the authoritative standard. This change aligns all tests to that standard without modifying production code.

Current Go version is 1.26 (`go.mod`), which provides `testing/synctest` for deterministic concurrency testing.

## Goals / Non-Goals

**Goals:**
- Full go-tester skill compliance across all 80 test files
- Reduced CI wall-clock time via `t.Parallel()` in mock-based tests
- Deterministic async tests via `synctest` (eliminate flaky timeouts)
- Consistent test setup patterns across all layers

**Non-Goals:**
- Increasing test coverage (adding new test cases for untested code paths)
- Refactoring production code
- Changing mock generation strategy or tooling
- Adding new test infrastructure (e.g., testcontainers, shared test utilities package)

## Decisions

### 1. `t.Parallel()` scope

**Decision**: Add `t.Parallel()` to all usecase and adapter layer tests. Do NOT add to `infrastructure/database/rdb/` tests.

**Rationale**: Usecase and adapter tests use mockery mocks — each subtest creates its own mock instances, so there is no shared mutable state. RDB tests share a single `testDB` connection and call `cleanDatabase()` between tests, making them inherently sequential.

**Alternative considered**: Making RDB tests parallel with per-test database schemas — rejected as over-engineering for this change.

### 2. `synctest` migration strategy

**Decision**: Replace `time.After` in `concert_uc_test.go` (AsyncSearchNewConcerts and receivePublishedConcerts) with `synctest.Test` wrapping.

**Rationale**: `time.After(5 * time.Second)` is a real wall-clock wait that makes tests slow and potentially flaky. `synctest.Test` provides virtual time control where `time.After` resolves immediately when all goroutines are blocked.

**Pattern**:
```go
func TestAsyncSearchNewConcerts(t *testing.T) {
    synctest.Test(t, func(t *testing.T) {
        // ... setup mocks ...
        err := d.uc.AsyncSearchNewConcerts(ctx, artistID)
        assert.NoError(t, err)
        // Virtual time: goroutines complete deterministically
    })
}
```

### 3. Deps-struct unification

**Decision**: Introduce `artistTestDeps` struct in `artist_uc_test.go` matching the existing `concertTestDeps` pattern.

**Rationale**: `concert_uc_test.go` already uses this pattern successfully. The 4-line mock setup repeated 12 times in `artist_uc_test.go` is the exact boilerplate this pattern eliminates. Consistency across the usecase layer makes tests easier to read and maintain.

### 4. `cleanDatabase` signature change

**Decision**: Change `cleanDatabase()` to `cleanDatabase(t *testing.T)` with `t.Helper()`.

**Rationale**: When `cleanDatabase` panics (e.g., table doesn't exist after migration), the stack trace points to `setup_test.go` instead of the calling test. Adding `t.Helper()` fixes this. Using `t.Fatal` instead of `panic` also gives cleaner test failure output.

**Impact**: All RDB test files that call `cleanDatabase()` need to pass `t`. This is a mechanical change.

### 5. `assert.AnError` replacement

**Decision**: Replace `assert.AnError` with specific `apperr` errors only in usecase-layer tests where the error type matters for business logic. Keep `assert.AnError` in adapter-layer tests where only error propagation is being verified.

**Rationale**: In adapter tests, the handler's job is to propagate errors — the specific type is irrelevant. In usecase tests, the error type often drives behavior (e.g., `ErrNotFound` vs `ErrInternal` may trigger different paths).

## Risks / Trade-offs

- **`t.Parallel()` may expose hidden shared state** → Mitigation: Run `go test -race -count=10` after adding parallelism to catch data races
- **`synctest` is new (Go 1.24+)** → Mitigation: Already using Go 1.26; `synctest` is stable and the team's go-tester skill already mandates it
- **`cleanDatabase(t)` signature change touches many files** → Mitigation: Mechanical find-and-replace, low risk of logic errors
- **Placeholder test for ConcertHandler.List needs understanding of handler logic** → Mitigation: Read the handler implementation to write meaningful assertions; follow `artist_handler_test.go` as the reference pattern
