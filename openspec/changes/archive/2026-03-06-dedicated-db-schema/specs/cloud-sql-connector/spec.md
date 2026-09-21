## MODIFIED Requirements

### Requirement: Standard Connection for Local

The application SHALL use standard `pgx` connection when running locally.

#### Scenario: Local Environment

- **WHEN** `ENVIRONMENT` is `local`
- **THEN** application uses standard TCP connection
- **AND** Uses `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_PASSWORD` (if provided)
- **AND** the DSN SHALL include `search_path` set to the configured `DATABASE_SCHEMA`

### Requirement: The system MUST support configurable database schema

The application SHALL accept a `DATABASE_SCHEMA` environment variable to control which PostgreSQL schema is used. The default value SHALL be `app`.

#### Scenario: Schema specified via environment variable

- **WHEN** `DATABASE_SCHEMA` is set to `app`
- **THEN** the DSN `search_path` parameter SHALL be set to `app,public`
- **AND** all unqualified table references SHALL resolve to the `app` schema

#### Scenario: Schema not specified

- **WHEN** `DATABASE_SCHEMA` is not set
- **THEN** the DSN `search_path` parameter SHALL default to `app,public`
- **AND** existing behavior SHALL be preserved
