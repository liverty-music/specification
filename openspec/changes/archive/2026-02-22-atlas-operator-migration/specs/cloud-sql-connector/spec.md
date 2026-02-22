## MODIFIED Requirements

### Requirement: Standard Connection for Local

The application SHALL use standard `pgx` connection when running locally.

#### Scenario: Local Environment

- **WHEN** `ENVIRONMENT` is `local`
- **THEN** application uses standard TCP connection
- **AND** Uses `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_PASSWORD` (if provided)
- **AND** DSN SHALL include `search_path` set to the value of `DATABASE_SCHEMA` (default: `public`)

## REMOVED Requirements

### Requirement: The system MUST provide a standard sql.DB connection for migrations

**Reason**: Migrations are no longer executed by the application. The Atlas Kubernetes Operator handles migration execution using its own database connection as the `postgres` user.

**Migration**: Remove `NewMigrationDB()` and related goose integration from the `rdb` package. The Atlas Operator manages migration connectivity independently.

## ADDED Requirements

### Requirement: Database schema SHALL be configurable via environment variable

The application SHALL read the `DATABASE_SCHEMA` environment variable to set the PostgreSQL `search_path` in its DSN. The default value SHALL be `public` for local development compatibility.

#### Scenario: Cloud environment with dedicated schema

- **WHEN** `DATABASE_SCHEMA` is set to `app`
- **THEN** the DSN SHALL include `search_path=app`
- **AND** all queries SHALL target the `app` schema

#### Scenario: Local environment with default schema

- **WHEN** `DATABASE_SCHEMA` is not set
- **THEN** the DSN SHALL default to `search_path=public`
- **AND** local development works without schema configuration
