# Spec: Cloud SQL Connector

## Purpose

Secure and efficient connectivity to Google Cloud SQL using the Cloud SQL Go Connector.

## Requirements

### Requirement: Authenticate via Cloud SQL Connector

The application SHALL use the Cloud SQL Go Connector for database connectivity when `ENVIRONMENT` is NOT `local`.

#### Scenario: Non-local Environments

- **WHEN** `ENVIRONMENT` is `development`, `staging`, or `production`
- **AND** `DATABASE_INSTANCE_CONNECTION_NAME` is provided
- **THEN** application initializes `cloudsqlconn.Dialer`
- **AND** `pgx` uses this dialer to connect
- **AND** connection uses IAM Auth and Private IP

### Requirement: Standard Connection for Local

The application SHALL use standard `pgx` connection when running locally.

#### Scenario: Local Environment

- **WHEN** `ENVIRONMENT` is `local`
- **THEN** application uses standard TCP connection
- **AND** Uses `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_PASSWORD` (if provided)

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

### Requirement: Configuration Validation

The application SHALL validate that `InstanceConnectionName` is present if `ENVIRONMENT` is not local.

#### Scenario: Missing Connection Name

- **WHEN** `ENVIRONMENT` is not `local`
- **AND** `DATABASE_INSTANCE_CONNECTION_NAME` is empty
- **THEN** application fails to start with descriptive error
