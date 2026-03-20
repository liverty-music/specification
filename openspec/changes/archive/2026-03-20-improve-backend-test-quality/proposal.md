## Why

The backend test suite (80 test files) has grown organically and now shows inconsistencies against the go-tester skill standards: missing `t.Parallel()` in mock-based tests, `time.After` usage instead of `synctest`, placeholder handler tests with no assertions, boilerplate mock setup duplication, and minor hygiene issues. Aligning all tests to a single standard improves reliability, reduces CI time, and prevents future drift.

## What Changes

- Add `t.Parallel()` to all usecase and adapter layer tests that use mocks (no shared mutable state)
- Replace `time.After` timeouts in async tests with `testing/synctest` virtual time
- Implement actual handler logic tests for `ConcertHandler.List` (currently a placeholder)
- Unify usecase test setup to use deps-struct pattern (matching `concert_uc_test.go` style)
- Improve `cleanDatabase()` signature to accept `*testing.T` and call `t.Helper()`
- Replace `assert.AnError` with specific `apperr` error types where applicable
- Fix `logger, _ := logging.New()` to check errors consistently

## Capabilities

### New Capabilities

(none - this is a test-only refactoring with no new user-facing capabilities)

### Modified Capabilities

(none - no spec-level behavior changes, implementation-only improvements)

## Impact

- **Code**: ~30 test files across `internal/usecase/`, `internal/adapter/`, `internal/infrastructure/database/rdb/`, and `pkg/` directories
- **Dependencies**: Requires Go 1.26+ for `testing/synctest` (verify current go.mod version)
- **CI**: Test execution time should decrease due to parallel test execution
- **Risk**: Low - test-only changes, no production code modifications
