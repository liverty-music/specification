## Context

The backend application connects to Cloud SQL via `cloudsqlconn.Dialer` (IAM Auth + PSC) using `pgxpool`. 17 versioned migration SQL files exist in `internal/infrastructure/database/rdb/migrations/versions/` in Atlas format. CI applies these via `atlas migrate apply` CLI against a test database. However, no mechanism exists to apply them to the dev Cloud SQL instance, leaving all tables missing.

Key constraints:
- Cloud SQL uses IAM authentication via `cloudsqlconn` Go library (no passwords)
- The existing connection uses `pgxpool.Pool` (pgx native), not `database/sql`
- Atlas CLI cannot use `cloudsqlconn` directly (it only accepts URL strings)
- Migration files are up-only SQL (no rollback scripts)

## Goals / Non-Goals

**Goals:**
- Apply pending database migrations automatically on application startup
- Support both local (Docker Compose) and Cloud SQL (IAM Auth + PSC) environments
- Prevent concurrent migration execution when multiple pods start simultaneously
- Maintain compatibility with existing `atlas migrate apply` in CI

**Non-Goals:**
- Replacing Atlas as the migration authoring/CI tool
- Adding rollback (down migration) support
- Migrating staging or production environments (dev only for now)
- Changing the existing `pgxpool`-based application connection

## Decisions

### Decision 1: Use goose v3 as the runtime migration library

**Choice**: `github.com/pressly/goose/v3` Provider API

**Alternatives considered**:
- **Atlas Go SDK (low-level `migrate` package)**: `RevisionReadWriter` is in an internal package (`cmd/atlas/internal/migrate`), making it impossible to import. Would require reimplementing revision tracking from scratch.
- **Atlas `atlasexec` (CLI wrapper)**: Only accepts URL connection strings. Cannot use `cloudsqlconn.Dialer` for IAM authentication. Would require adding Cloud SQL Auth Proxy as a sidecar.
- **`golang-migrate/migrate` v4**: Requires `{version}_{name}.up.sql` / `.down.sql` file pairs. Incompatible with existing Atlas single-file format without restructuring.
- **Custom migration runner**: Would work but reinvents revision tracking, advisory locking, and checksum validation that goose already provides.

**Rationale**: goose accepts `*sql.DB` directly (compatible with `cloudsqlconn`), supports `embed.FS`, includes PostgreSQL advisory locking via `WithSessionLocker`, and requires only a `-- +goose Up` annotation added to existing SQL files (no content changes).

### Decision 2: Create a dedicated `*sql.DB` for migrations

**Choice**: Create a short-lived `*sql.DB` connection using `cloudsqlconn` + `pgx/v5/stdlib`, run migrations, then close it. The main application continues using `pgxpool.Pool`.

**Rationale**: goose requires `*sql.DB` (standard library interface). Mixing migration concerns into the main connection pool would complicate lifecycle management. A separate connection that closes after migration keeps concerns isolated.

### Decision 3: Run migrations after DB connection, before repository init

**Choice**: Insert migration execution in `InitializeApp()` between `rdb.New()` and repository creation.

```
InitializeApp(ctx)
  ├─ config.Load() + Validate()
  ├─ provideLogger()
  ├─ rdb.New(ctx, cfg, logger)          // establish connection
  ├─ rdb.RunMigrations(ctx, cfg, logger) // NEW: apply pending migrations
  ├─ provideRepositories(db)             // repositories need tables to exist
  └─ ...
```

**Rationale**: Migrations must complete before any repository tries to query tables. Running after `rdb.New()` confirms database connectivity first.

### Decision 4: Use PostgreSQL advisory lock for concurrency safety

**Choice**: goose's `WithSessionLocker` using `lock.NewPostgresSessionLocker()`.

**Rationale**: PostgreSQL advisory locks (`pg_advisory_lock`) are session-scoped and automatically released on disconnect. No external infrastructure (Redis, etc.) required. This is the standard approach used by Atlas, goose, and golang-migrate.

### Decision 5: Embed migration files with `go:embed`

**Choice**: Use `//go:embed` to bundle migration SQL files into the Go binary.

**Rationale**: Eliminates runtime filesystem dependency. The Docker container does not need to include the migration files separately. Ensures migration files are always consistent with the application version.

## Risks / Trade-offs

- **[Dual migration tooling]** CI uses `atlas migrate apply`, runtime uses `goose`. They track revisions in different tables (`atlas_schema_revisions` vs `goose_db_version`). → Both execute the same SQL files in the same order; the actual schema state is identical. Atlas in CI validates migration integrity; goose at runtime applies them.

- **[Startup latency]** Migrations add time to pod startup. → Negligible for already-applied migrations (goose checks version table, finds nothing pending, returns). Only first deployment has measurable overhead.

- **[Failed migration blocks startup]** A bad migration prevents all pods from starting. → This is intentional — running with an inconsistent schema would cause worse failures. Fix the migration and redeploy.

- **[Advisory lock timeout]** If a migration takes very long, other pods wait. → Set a reasonable lock timeout (e.g., 30s). Migrations in this project are lightweight DDL operations.

## Migration Plan: goose → Atlas Operator (Future)

This design intentionally uses goose v3 as a stepping stone. The long-term target is the **Atlas Kubernetes Operator** with Atlas Cloud Registry, which provides declarative, GitOps-native migration management.

### Why not Atlas Operator now

- Atlas Operator requires infrastructure setup (Helm install, Workload Identity binding for the operator SA, Atlas Cloud account + Bot Token)
- The immediate priority is unblocking dev — goose solves this with zero infrastructure changes

### Atlas Operator architecture (target state)

```
┌──────────────┐     ┌───────────────────┐     ┌──────────────┐
│ Git Push     │────▶│ Atlas Cloud       │     │ GKE Cluster  │
│ (CI syncs    │     │ Schema Registry   │◀────│ Atlas        │
│  migrations) │     │ (versioned dir)   │     │ Operator     │
└──────────────┘     └───────────────────┘     └──────┬───────┘
                                                       │
                                                       ▼
                                               ┌──────────────┐
                                               │ Cloud SQL    │
                                               │ (IAM Auth    │
                                               │  via gcp_    │
                                               │  cloudsql_   │
                                               │  token)      │
                                               └──────────────┘
```

The operator uses `gcp_cloudsql_token` data source for IAM authentication — no Cloud SQL Auth Proxy or `cloudsqlconn` needed:

```hcl
data "gcp_cloudsql_token" "db" {}
env {
  name = atlas.env
  url  = "postgres://sa:${urlescape(data.gcp_cloudsql_token.db)}@10.10.10.10:5432/backend-app?sslmode=require"
}
```

### Migration steps (goose → Atlas Operator)

1. **Remove goose code** from Go application (`migrate.go`, DI wiring, `go.mod` dependency)
2. **Remove `-- +goose Up` annotations** from all SQL migration files
3. **Install Atlas Operator** via Helm with `--set allowCustomConfig=true`
4. **Configure Workload Identity** for the Atlas Operator service account
5. **Create Atlas Cloud project**, generate Bot Token, store as K8s Secret
6. **Deploy AtlasMigration CRD** with `baseline` set to the current latest version (e.g., `20260221130000`) so Atlas skips all previously applied migrations
7. **Verify** — `kubectl get atlasmigration` should show `READY: True`
8. **Clean up** — optionally drop `goose_db_version` table from Cloud SQL

### Revision table coexistence

| Environment | Tool | Table | Lifecycle |
|---|---|---|---|
| CI test DB | `atlas migrate apply` | `atlas_schema_revisions` | Created and destroyed per test run |
| Dev Cloud SQL (Phase 1) | goose | `goose_db_version` | Persistent during goose era |
| Dev Cloud SQL (Phase 2) | Atlas Operator | `atlas_schema_revisions` | Persistent; baseline skips goose-applied versions |

The two revision tables (`goose_db_version` and `atlas_schema_revisions`) never coexist in the same environment during active use. Atlas's `baseline` flag ensures it does not re-apply migrations that goose already applied.
