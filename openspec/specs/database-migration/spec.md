# database-migration Specification

## Purpose

Automated database schema migration on application startup using goose v3, ensuring the database schema is always up to date before serving traffic.

## Requirements

### Requirement: The system MUST apply pending database migrations on startup

The backend application SHALL execute all pending SQL migration files before serving any traffic. Migrations SHALL be applied using goose v3 Provider API with embedded SQL files.

#### Scenario: First deployment with empty database

- **WHEN** the application starts against a database with no tables
- **THEN** all migration files SHALL be applied in version order
- **AND** the application SHALL proceed to serve requests after all migrations succeed

#### Scenario: Subsequent startup with up-to-date schema

- **WHEN** the application starts against a database where all migrations are already applied
- **THEN** no migration files SHALL be executed
- **AND** startup SHALL not be delayed beyond the version check

#### Scenario: New migrations available

- **WHEN** the application starts with a newer binary containing additional migration files
- **THEN** only the pending (unapplied) migration files SHALL be executed
- **AND** previously applied migrations SHALL not be re-executed

### Requirement: The system MUST prevent concurrent migration execution

When multiple application instances start simultaneously, only one instance SHALL execute migrations. Other instances SHALL wait until migration completes before proceeding.

#### Scenario: Two pods start simultaneously

- **WHEN** Pod A and Pod B start at the same time
- **THEN** one pod SHALL acquire a PostgreSQL advisory lock
- **AND** the other pod SHALL wait for the lock to be released
- **AND** the waiting pod SHALL find no pending migrations after acquiring the lock
- **AND** both pods SHALL eventually start serving traffic

### Requirement: The system MUST fail startup on migration error

If any migration file fails to execute, the application SHALL terminate with a descriptive error. The system SHALL NOT serve traffic with an inconsistent database schema.

#### Scenario: Invalid SQL in migration file

- **WHEN** a migration file contains invalid SQL
- **THEN** the application SHALL log the error with the file name and SQL statement
- **AND** the application SHALL exit with a non-zero status code
- **AND** the advisory lock SHALL be released

### Requirement: The system MUST embed migration files in the binary

Migration SQL files SHALL be embedded into the Go binary using `go:embed`. The application SHALL NOT depend on migration files being present on the filesystem at runtime.

#### Scenario: Container without migration files on disk

- **WHEN** the application binary runs in a container without the source migration directory
- **THEN** migrations SHALL still execute correctly from the embedded filesystem

### Requirement: The CI pipeline MUST validate migration file ordering

The atlas-ci workflow SHALL verify that all new migration files have timestamps greater than the latest migration version on the base branch. PRs with out-of-order migrations SHALL fail CI.

#### Scenario: PR with out-of-order migration file

- **WHEN** a PR adds a migration file with a timestamp earlier than the latest on `origin/main`
- **THEN** the atlas-ci job SHALL fail with a descriptive error message
- **AND** the error message SHALL suggest running `scripts/check-migration-drift.sh --fix`

#### Scenario: PR with correctly ordered migration file

- **WHEN** a PR adds a migration file with a timestamp later than the latest on `origin/main`
- **THEN** the atlas-ci job SHALL pass the ordering check
