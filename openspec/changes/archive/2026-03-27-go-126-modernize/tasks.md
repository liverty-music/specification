## 1. Automated Modernization (`go fix`)

- [x] 1.1 Run `go fix ./...` to apply all modernizer analyzers (`interface{}→any`, `for→range int`, `wg.Go`, `slices.Contains`, `new(value)`, `//go:fix inline`)
- [x] 1.2 Remove dead pointer-helper functions (`strPtr`, `floatPtr`, `statusPtr`) that `go fix` inlined with `new(value)`
- [x] 1.3 Run `go vet ./...` and `go build ./...` to verify no compilation errors

## 2. `errors.AsType[T]` Migration

- [x] 2.1 Migrate `errors.As` → `errors.AsType[T]` in `internal/infrastructure/database/rdb/errors.go` (3 call sites: `toAppErr`, `IsForeignKeyViolation`, `IsUniqueViolation`)
- [x] 2.2 Migrate `errors.As` → `errors.AsType[T]` in `internal/infrastructure/gcp/gemini/errors.go` (4 call sites: `toAppErr` for `genai.APIError`, `*json.SyntaxError`, `*json.UnmarshalTypeError`; `isRetryable` for `genai.APIError`)
- [x] 2.3 Migrate `errors.As` → `errors.AsType[T]` in `internal/infrastructure/blockchain/ticketsbt/client.go` (1 of 2 call sites: `rpc.DataError`; anonymous interface kept as `errors.As`)
- [x] 2.4 Update test assertions in `gemini/errors_internal_test.go` to use `errors.AsType[T]` (2 call sites)

## 3. Standard Library Adoption

- [x] 3.1 Replace `BestByLikes` manual max loop with `slices.MaxFunc` in `internal/entity/fanart.go`
- [x] 3.2 Convert `ScrapedConcert.StartTime` and `ScrapedConcert.OpenTime` from `*time.Time` + `omitempty` to `time.Time` + `omitzero`
- [x] 3.3 Update `ScrapedConcert.ToConcert()` to map `time.Time` zero values back to `*time.Time` nil for `entity.Event`
- [x] 3.4 Update all `ScrapedConcert` construction sites in tests and production code to use `time.Time` instead of `*time.Time`

## 4. CI Enforcement

- [x] 4.1 Add `modernize` target to Makefile: `go fix -diff ./...` with non-zero exit on diff
- [x] 4.2 Insert `modernize` into `check` target between `lint-schema` and `test`

## 5. Verification

- [x] 5.1 Run `make check` (lint + lint-schema + modernize + test) — all must pass
- [x] 5.2 Run `go fix -diff ./...` and confirm zero output (no remaining modernization opportunities)
