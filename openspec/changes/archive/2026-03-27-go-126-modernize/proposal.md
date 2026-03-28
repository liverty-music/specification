## Why

Go 1.26 introduces language-level improvements (`new(value)`, `errors.AsType[T]`), standard library additions (`sync.WaitGroup.Go`, `slices.Contains` modernizer), and toolchain enhancements (`go fix` with 20+ analyzers). The backend already uses `go 1.26` in go.mod but the codebase still uses pre-1.26 patterns. Modernizing now ensures consistency, eliminates boilerplate, and captures free performance wins (Green Tea GC, `io.ReadAll` 2x speedup).

## What Changes

- Apply `go fix ./...` to auto-modernize ~25 call sites: `interface{}` → `any`, C-style `for` → `range int`, `wg.Add+go func` → `wg.Go`, manual loops → `slices.Contains`, pointer helpers → `new(value)`
- Migrate all 11 `errors.As` call sites to `errors.AsType[T]` for compile-time type safety and ~3x performance
- Replace `BestByLikes` manual loop with `slices.MaxFunc`
- Convert `*time.Time + omitempty` fields to `time.Time + omitzero` where `IsZero()` semantics apply
- Add `modernize` target to Makefile to enforce `go fix` compliance in `make check`

## Capabilities

### New Capabilities

(none — pure refactoring, no new capabilities)

### Modified Capabilities

(none — no spec-level behavior changes)

## Impact

- **Backend code**: ~40 files across entity, infrastructure, adapter, and pkg layers
- **Makefile**: New `modernize` target added to `check` pipeline
- **DB layer**: `*time.Time` → `time.Time` changes require corresponding `pgx` scan adjustments (nullable columns use `pgtype.Timestamptz`)
- **Tests**: All existing tests validate correctness; no new test logic needed
- **CI**: `make check` gains `go fix -diff` enforcement — new code using old patterns will fail CI
- **Dependencies**: No new external dependencies; uses only Go standard library
