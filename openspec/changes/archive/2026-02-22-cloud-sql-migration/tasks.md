## 1. Dependencies and Migration File Preparation

- [x] 1.1 Add `github.com/pressly/goose/v3` to `go.mod`
- [x] 1.2 Add `-- +goose Up` annotation to the first line of all 17 migration SQL files in `internal/infrastructure/database/rdb/migrations/versions/`
- [x] 1.3 Regenerate `atlas.sum` by running `atlas migrate hash` to account for the annotation changes

## 2. Migration Connection (`*sql.DB` via cloudsqlconn)

- [x] 2.1 Add `NewStdlibDB` function to `internal/infrastructure/database/rdb/postgres.go` that creates a `*sql.DB` using `pgx/v5/stdlib` with the same `cloudsqlconn.Dialer` configuration (IAM Auth + PSC for non-local, direct TCP for local)

## 3. Migration Runner

- [x] 3.1 Create `internal/infrastructure/database/rdb/migrate.go` with `//go:embed` directive for `migrations/versions/*.sql`
- [x] 3.2 Implement `RunMigrations(ctx, cfg, logger)` function using goose v3 Provider API with `WithSessionLocker` (PostgreSQL advisory lock) and the embedded FS
- [x] 3.3 Add structured logging for migration start, each applied file, and completion

## 4. DI Integration

- [x] 4.1 Modify `internal/di/provider.go` `InitializeApp()` to call `rdb.RunMigrations()` after `rdb.New()` and before repository initialization

## 5. Verification

- [x] 5.1 Verify local: `docker compose up postgres` then `go run cmd/api/main.go` — confirm tables are created and goose_db_version table exists
- [x] 5.2 Verify idempotency: restart the application — confirm no migrations are re-applied
- [x] 5.3 Run existing CI tests (`go test ./...`) to confirm no regressions
- [x] 5.4 Verify `atlas migrate apply` still works in CI (atlas ignores `-- +goose Up` as a comment)
