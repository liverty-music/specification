## ADDED Requirements

### Requirement: SERIAL and BIGSERIAL detection
The schema linter SHALL detect usage of `SERIAL` or `BIGSERIAL` types in `schema.sql` and report an error.

#### Scenario: Schema contains SERIAL column
- **WHEN** `schema.sql` contains a column defined with `SERIAL` or `BIGSERIAL`
- **THEN** the linter SHALL exit with code 1 and print the violating line number and content

#### Scenario: Schema has no SERIAL columns
- **WHEN** `schema.sql` contains no `SERIAL` or `BIGSERIAL` usage
- **THEN** the linter SHALL pass this check without error

### Requirement: Bare TIMESTAMP detection
The schema linter SHALL detect usage of `TIMESTAMP` (without time zone) in `schema.sql` and report an error. The pattern `\bTIMESTAMP\b` SHALL be used, which does not match `TIMESTAMPTZ`.

#### Scenario: Schema contains bare TIMESTAMP
- **WHEN** `schema.sql` contains a column defined with `TIMESTAMP` (not `TIMESTAMPTZ`)
- **THEN** the linter SHALL exit with code 1 and print the violating line number and content

#### Scenario: Schema uses TIMESTAMPTZ correctly
- **WHEN** `schema.sql` uses only `TIMESTAMPTZ` for temporal columns
- **THEN** the linter SHALL pass this check without error

### Requirement: Audit column detection
The schema linter SHALL detect `created_at`, `updated_at`, or `deleted_at` columns in `schema.sql` and report an error.

#### Scenario: Schema contains audit columns
- **WHEN** `schema.sql` contains a column named `created_at`, `updated_at`, or `deleted_at`
- **THEN** the linter SHALL exit with code 1 and print the violating line number and content

#### Scenario: Schema has no audit columns
- **WHEN** `schema.sql` contains no audit columns
- **THEN** the linter SHALL pass this check without error

### Requirement: VARCHAR detection
The schema linter SHALL detect usage of `VARCHAR(n)` in `schema.sql` and report an error. The project convention is `TEXT` with `CHECK` constraints for length enforcement.

#### Scenario: Schema contains VARCHAR column
- **WHEN** `schema.sql` contains a column defined with `VARCHAR(`
- **THEN** the linter SHALL exit with code 1 and print the violating line number and content

#### Scenario: Schema uses TEXT with CHECK
- **WHEN** `schema.sql` uses `TEXT` type with `CHECK` constraints for length validation
- **THEN** the linter SHALL pass this check without error

### Requirement: COMMENT ON TABLE coverage
The schema linter SHALL verify that every `CREATE TABLE` statement has a corresponding `COMMENT ON TABLE` statement.

#### Scenario: Table missing COMMENT ON TABLE
- **WHEN** `schema.sql` defines a table via `CREATE TABLE` without a matching `COMMENT ON TABLE`
- **THEN** the linter SHALL exit with code 1 and report the table name

#### Scenario: All tables have comments
- **WHEN** every `CREATE TABLE` in `schema.sql` has a corresponding `COMMENT ON TABLE`
- **THEN** the linter SHALL pass this check without error

### Requirement: COMMENT ON COLUMN coverage
The schema linter SHALL verify that the number of columns defined in each table matches the number of `COMMENT ON COLUMN` statements for that table.

#### Scenario: Table has missing column comments
- **WHEN** a table in `schema.sql` has more column definitions than `COMMENT ON COLUMN` statements
- **THEN** the linter SHALL exit with code 1 and report the table name with expected and actual counts

#### Scenario: All columns have comments
- **WHEN** every column in every table has a corresponding `COMMENT ON COLUMN`
- **THEN** the linter SHALL pass this check without error

### Requirement: Makefile integration
The schema linter SHALL be invocable via `make lint-schema` and SHALL be included in `make check`.

#### Scenario: make check runs schema lint
- **WHEN** a developer runs `make check`
- **THEN** `lint-schema` SHALL execute as part of the check pipeline

#### Scenario: make lint-schema runs standalone
- **WHEN** a developer runs `make lint-schema`
- **THEN** the schema linter script SHALL execute and report results

### Requirement: CI integration
The schema linter SHALL run in CI via `lint.yml` when `schema.sql` is modified.

#### Scenario: PR modifies schema.sql
- **WHEN** a pull request modifies `schema.sql`
- **THEN** the `schema-lint` CI job SHALL run and report results

#### Scenario: PR does not modify schema.sql
- **WHEN** a pull request does not modify `schema.sql`
- **THEN** the `schema-lint` CI job SHALL be skipped

### Requirement: Comment-line exclusion
The schema linter SHALL ignore SQL comment lines (lines starting with `--`) when checking for pattern violations.

#### Scenario: Prohibited keyword appears only in comment
- **WHEN** `schema.sql` contains `-- Use SERIAL for legacy tables` as a comment
- **THEN** the linter SHALL NOT report this as a violation

#### Scenario: Prohibited keyword appears in active SQL
- **WHEN** `schema.sql` contains `id SERIAL PRIMARY KEY` as active SQL
- **THEN** the linter SHALL report this as a violation

## MODIFIED Requirements

### Requirement: Database migration workflow includes schema lint
The `make check` target SHALL include `lint-schema` in addition to `lint` and `test`.

#### Scenario: make check target composition
- **WHEN** a developer runs `make check`
- **THEN** `lint`, `lint-schema`, and `test` SHALL all execute
