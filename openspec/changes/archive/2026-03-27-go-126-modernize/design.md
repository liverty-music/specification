## Context

The backend (`go 1.26` in go.mod) uses pre-1.26 idioms throughout ~40 files. Go 1.26 introduced language changes (`new(value)`), new standard library APIs (`errors.AsType[T]`, `sync.WaitGroup.Go`), and the `go fix` modernizer tool with 20+ analyzers. The codebase has not yet adopted these.

Key patterns to modernize:
- 11 `errors.As` call sites (rdb, gemini, blockchain layers)
- `interface{}` instead of `any` (cache, test helpers)
- C-style `for i := 0; i < n` instead of `range int`
- Manual `wg.Add(1) + go func() { defer wg.Done() }` pattern
- Manual issuer-matching loop instead of `slices.Contains`
- Pointer-helper functions (`strPtr`, `floatPtr`) instead of `new(value)`
- `*time.Time` with `omitempty` on JSON-tagged event payloads

## Goals / Non-Goals

**Goals:**
- Adopt Go 1.26 idioms across the entire backend codebase
- Enforce modern patterns in CI via `go fix -diff` check
- Eliminate pointer-helper boilerplate in tests using `new(value)`
- Gain compile-time type safety on error unwrapping via `errors.AsType[T]`

**Non-Goals:**
- Adopt `encoding/json/v2` (still experimental, `GOEXPERIMENT` required)
- Change `*time.Time` fields on `entity.Event` (no json tags; DB scan depends on pointer nil semantics)
- Refactor existing architecture or add new features
- Adopt experimental packages (`simd`, `runtime/secret`, goroutine leak profiler)

## Decisions

### D1: Apply `go fix ./...` as a single batch

**Decision**: Run `go fix ./...` to apply all modernizer analyzers at once.

**Rationale**: The tool is idempotent, produces minimal diffs, and all transformations are semantics-preserving. Cherry-picking individual analyzers adds process overhead with no safety benefit. All 20+ analyzers (interface→any, rangeint, waitgroup, slicescontains, newptr, etc.) produce correct output.

**Alternative considered**: Run analyzers one-by-one (`go fix -omitzero ./...`, `go fix -forvar ./...`). Rejected — unnecessary granularity for a batch refactor.

### D2: `errors.AsType[T]` migration (manual, not auto-fixable)

**Decision**: Replace all 11 `errors.As` calls with `errors.AsType[T]`.

**Rationale**: `go fix` does not auto-rewrite `errors.As` → `errors.AsType` because the semantics differ slightly (AsType is generic and cannot target interface types). All 11 call sites in this codebase target concrete pointer types (`*pgconn.PgError`, `genai.APIError`, `*json.SyntaxError`, etc.), making the migration safe.

**Pattern**:
```go
// Before
var pgErr *pgconn.PgError
if errors.As(err, &pgErr) { ... }

// After
if pgErr, ok := errors.AsType[*pgconn.PgError](err); ok { ... }
```

### D3: `omitzero` scope limited to `ScrapedConcert` JSON fields

**Decision**: Only convert `*time.Time` + `omitempty` to `time.Time` + `omitzero` on `ScrapedConcert` (the JSON event payload struct). Do NOT touch `entity.Event.StartTime`/`OpenTime`.

**Rationale**:
- `ScrapedConcert` uses json tags for NATS event serialization. `omitzero` with `time.Time.IsZero()` correctly omits zero times.
- `entity.Event` has no json tags — `*time.Time` is used for DB NULL semantics via pgx. Changing this would cascade into repository scan logic across concert_repo, venue_repo, and ticket_email_repo.
- `LogoColorProfile.DominantHue` (`*float64`) stays as-is: `float64(0)` is a valid hue angle (red), so `omitzero` would incorrectly omit it.
- `ScrapedConcert.AdminArea` (`*string`) stays as `*string + omitempty`: empty string `""` is a valid admin area value, so `omitzero` would omit valid data.

### D4: `slices.MaxFunc` for `BestByLikes`

**Decision**: Replace the manual max-finding loop in `BestByLikes` with `slices.MaxFunc`.

**Rationale**: Direct 1:1 replacement. The function already handles the empty-slice edge case with an early return, which `slices.MaxFunc` would panic on, so the guard stays.

### D5: `modernize` Makefile target with CI enforcement

**Decision**: Add a `modernize` target that runs `go fix -diff ./...` and fails if output is non-empty. Insert it into `check` between `lint-schema` and `test`.

**Rationale**: Prevents new code from regressing to old patterns. The check is fast (uses Go analysis framework, no compilation), idempotent, and tied to the Go version in go.mod. Developers run `go fix ./...` to auto-fix any violations.

## Risks / Trade-offs

**[`new(value)` readability]** → Some developers find `new("lost")` less readable than `strPtr("lost")`. Mitigated: `new(value)` is now idiomatic Go 1.26 and `go fix` will continue to suggest it. The `//go:fix inline` directive on old helper functions guides tooling.

**[`omitzero` on `ScrapedConcert.StartTime`/`OpenTime`]** → Changing from `*time.Time` to `time.Time` means consumers receiving the JSON payload will see `"0001-01-01T00:00:00Z"` if serialized without `omitzero`, instead of field absence. Mitigated: `omitzero` correctly omits zero-value `time.Time`, and the consumer (`concert_consumer.go`) uses the `ScrapedConcert.ToConcert()` method which maps back to `*time.Time` on `entity.Event`.

**[`go fix` version coupling]** → The `modernize` CI target depends on the Go toolchain version. If CI and local differ, `go fix -diff` may produce different results. Mitigated: Go version is pinned via `go.mod` and the CI uses the same version from the `go` directive.

**[`errors.AsType` on `genai.APIError`]** → `genai.APIError` is a value type (not a pointer). `errors.AsType[genai.APIError]` works correctly for value-receiver error types. Verified in the current code — `errors.As(err, &apiErr)` already uses a value variable.
