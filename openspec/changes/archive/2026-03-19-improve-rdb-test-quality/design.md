## Context

The `rdb` package contains 17 production files and 12 test files. Tests are integration tests against a real PostgreSQL instance. The codebase has grown organically, resulting in inconsistent patterns across test files written at different times. The go-tester skill defines clear standards (table-driven tests, `wantErr error`, no `time.Sleep`, black-box `_test` package) that are mostly followed but with notable exceptions.

Current state:
- 2 repositories have zero test coverage (`PushSubscriptionRepository`, `TicketJourneyRepository`)
- ~15 interface methods with documented possible errors lack direct test cases
- Pointer helpers are duplicated (`strPtr` in venue, `ptr[T]` in concert, no shared version)
- Seed data is created via raw SQL INSERT in each test file independently
- `cleanTables()` is missing the `push_subscriptions` table
- `search_log_repo_test.go` uses `time.Sleep` and sequential-dependent subtests

## Goals / Non-Goals

**Goals:**
- Every repository interface method has at least one test per documented possible error code
- All test files follow the same structural patterns (go-tester skill compliant)
- Shared seed helpers eliminate raw SQL duplication across test files
- Zero go-tester skill violations

**Non-Goals:**
- Context cancellation / connection failure testing (requires error injection, out of scope)
- Concurrent access / race condition testing
- Performance benchmarking of queries
- Changing production code or SQL queries
- Adding test coverage for `traced_pool.go` beyond what already exists

## Decisions

### D1: Canonical test structure

All table-driven tests will follow this pattern:

```go
func TestXxxRepository_MethodName(t *testing.T) {
    repo := rdb.NewXxxRepository(testDB)
    ctx := context.Background()

    type args struct { /* method params */ }

    tests := []struct {
        name    string
        setup   func()
        args    args
        want    *Expected // or appropriate type
        wantErr error
    }{...}

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            if tt.setup != nil {
                tt.setup()
            }
            // call method
            if tt.wantErr != nil {
                assert.ErrorIs(t, err, tt.wantErr)
                return
            }
            require.NoError(t, err)
            // assertions
        })
    }
}
```

Rationale: Matches go-tester skill example exactly. Using `tt` (not `tc`), named `type args struct` (not anonymous), `wantErr error` (not `bool`), single `assert.ErrorIs` (not `require.Error` + `assert.ErrorIs`).

### D2: Each test case calls `cleanDatabase()` via `setup`

Every test case's `setup` function starts with `cleanDatabase()`. No test case depends on state from a previous case.

Rationale: Eliminates ordering dependencies. A single failing case won't cascade. Slightly slower but much more maintainable.

Alternative considered: Transaction-per-test with rollback. Rejected because some repos use transactions internally, and nested transactions add complexity.

### D3: Shared seed helpers in `setup_test.go`

Extract reusable helpers:

```go
func seedUser(t *testing.T, name, email, externalID string) string       // returns userID
func seedArtist(t *testing.T, name, mbid string) string                   // returns artistID
func seedVenue(t *testing.T, name string) string                          // returns venueID
func seedEvent(t *testing.T, venueID, artistID, title, date string) string // returns eventID
```

Each calls `t.Helper()` and uses `uuid.NewV7()` for IDs. All raw SQL INSERT statements in individual test files will be replaced with these helpers.

Rationale: DRY. Currently 6+ test files have near-identical `INSERT INTO users` / `INSERT INTO artists` SQL. Changes to schema (e.g., adding a required column) would require updating every test file.

Alternative considered: Using the repository's own `Create` method for seeding. Rejected because we don't want test setup to depend on the code under test — if `Create` has a bug, all tests that use it for seeding would fail misleadingly.

### D4: Single generic `ptr[T]` helper

Replace `strPtr()` (venue_repo_test.go) with a single generic helper in `setup_test.go`:

```go
func ptr[T any](v T) *T { return &v }
```

Rationale: Go 1.18+ generics make `strPtr`, `intPtr`, etc. unnecessary. One helper covers all types.

### D5: Eliminate `time.Sleep` in search_log tests

The timestamp ordering test currently sleeps 10ms to ensure `searched_at` differs. Replace with explicit timestamp comparison: assert that `logAfter.SearchTime` is `>=` `logBefore.SearchTime` (which is already the assertion). The sleep is redundant because the DB uses `now()` which advances between statements.

If precise ordering is needed, inject a known timestamp via raw SQL rather than relying on wall-clock timing.

### D6: `cleanTables()` completeness

Add `push_subscriptions` to the table list in `cleanTables()`. Position it before `users` (due to FK user_id).

## Risks / Trade-offs

- **Test execution time**: Adding ~30+ new test cases and per-case `cleanDatabase()` will increase test runtime. Mitigation: TRUNCATE CASCADE is fast on small test datasets. If it becomes a problem, batch multiple TRUNCATE statements into a single SQL call.
- **Large diff**: Normalizing all 12 test files produces a big PR. Mitigation: Changes are mechanical and reviewable by pattern. No production code changes.
- **Seed helper coupling**: Shared helpers in `setup_test.go` create a single point of change. Mitigation: This is intentional — schema changes should be reflected in one place, not scattered.
