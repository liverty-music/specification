## Why

After fixing authentication (cloud-provisioning#86), the dev Cloud SQL instance returns `500 Internal Server Error` on all API calls because required tables do not exist (`relation "artists" does not exist`). 17 migration SQL files exist in the backend repo but there is no mechanism to apply them to Cloud SQL. Users can authenticate but cannot use any feature.

## What Changes

- Add a database migration runner that executes on application startup before serving requests
- Integrate `goose` v3 as the migration library, using its Provider API with PostgreSQL advisory locking
- Annotate existing Atlas-format migration SQL files with `-- +goose Up` directive for compatibility
- Create a short-lived `*sql.DB` connection (via `cloudsqlconn`) dedicated to migration execution
- Wire migration execution into the DI startup sequence between database connection and repository initialization

## Capabilities

### New Capabilities
- `database-migration`: Automated schema migration mechanism that applies pending SQL migrations on application startup using goose v3, with advisory lock protection for concurrent pod safety

### Modified Capabilities
- `cloud-sql-connector`: Add a method to create a standard `*sql.DB` connection (alongside existing `pgxpool`) for use by the migration runner
- `database`: Add requirement that schema migrations are applied automatically before the application serves traffic

## Impact

- **Backend repo**: New `migrate.go` file in `internal/infrastructure/database/rdb/`, modifications to `postgres.go` and `internal/di/provider.go`
- **Dependencies**: `github.com/pressly/goose/v3` added to `go.mod`
- **Migration files**: All 17 existing `.sql` files get a `-- +goose Up` annotation prepended (no SQL logic changes)
- **CI**: Existing `atlas migrate apply` in test workflow continues to work (atlas ignores goose annotations as comments)
- **Deployment**: No infrastructure changes needed — migrations run inside the existing backend pod
