## ADDED Requirements

### Requirement: The system MUST provide a standard sql.DB connection for migrations

The `rdb` package SHALL expose a function to create a short-lived `*sql.DB` connection using the same `cloudsqlconn.Dialer` configuration as the main `pgxpool.Pool`. This connection SHALL be used exclusively by the migration runner and closed after migrations complete.

#### Scenario: Non-local environment migration connection

- **WHEN** the migration runner needs a database connection in a non-local environment
- **THEN** a `*sql.DB` SHALL be created using `pgx/v5/stdlib` with `cloudsqlconn.Dialer`
- **AND** the connection SHALL use IAM authentication and PSC
- **AND** the connection SHALL be closed after migrations complete

#### Scenario: Local environment migration connection

- **WHEN** the migration runner needs a database connection in a local environment
- **THEN** a `*sql.DB` SHALL be created using standard TCP connection via DSN
- **AND** no `cloudsqlconn.Dialer` SHALL be initialized
