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
- **AND** DSN SHALL include `search_path` set to the value of `DATABASE_SCHEMA` (default: `public`)

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

### Requirement: Configuration Validation

The application SHALL validate that `InstanceConnectionName` is present if `ENVIRONMENT` is not local.

#### Scenario: Missing Connection Name

- **WHEN** `ENVIRONMENT` is not `local`
- **AND** `DATABASE_INSTANCE_CONNECTION_NAME` is empty
- **THEN** application fails to start with descriptive error
