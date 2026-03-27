# Database Trace Correlation

## MODIFIED Requirements

### Requirement: OTel span creation for database queries
The system SHALL create an OpenTelemetry child span for every database query executed through the connection pool, capturing the SQL operation, query text, execution duration, and additional Semantic Convention attributes including table name, database namespace, server address, and PostgreSQL error codes.

#### Scenario: SELECT query creates a client span
- **WHEN** a repository method executes a SELECT query via the pool wrapper
- **THEN** an OTel span SHALL be created with kind `Client`
- **AND** the span name SHALL be the SQL operation name (e.g., `SELECT`)
- **AND** the span SHALL have attribute `db.system` set to `postgresql`
- **AND** the span SHALL have attribute `db.query.text` set to the original SQL text (without injected comments)
- **AND** the span SHALL have attribute `db.operation.name` set to the extracted operation
- **AND** the span SHALL have attribute `db.collection.name` set to the primary table name extracted from the SQL (e.g., `concerts` from `SELECT ... FROM concerts`)
- **AND** the span SHALL have attribute `db.namespace` set to the database name
- **AND** the span SHALL have attribute `server.address` set to the database host

#### Scenario: INSERT query creates a client span
- **WHEN** a repository method executes an INSERT query via the pool wrapper
- **THEN** an OTel span SHALL be created with span name `INSERT`
- **AND** the span SHALL have attribute `db.collection.name` set to the target table name (e.g., `artists` from `INSERT INTO artists`)
- **AND** the span SHALL record the duration of the query execution

#### Scenario: Query execution error records PostgreSQL error code
- **WHEN** a database query fails with a `*pgconn.PgError`
- **THEN** the span SHALL record the error
- **AND** the span status SHALL be set to `Error`
- **AND** the span SHALL have attribute `db.response.status_code` set to the PostgreSQL error code (e.g., `23505` for unique violation)

#### Scenario: Query execution error without PgError
- **WHEN** a database query fails with a non-PostgreSQL error (e.g., context cancellation)
- **THEN** the span SHALL record the error
- **AND** the span status SHALL be set to `Error`
- **AND** the `db.response.status_code` attribute SHALL NOT be set

#### Scenario: Table name extraction fails gracefully
- **WHEN** a query uses complex SQL (CTEs, subqueries, dynamic SQL) where table name extraction is not possible
- **THEN** the `db.collection.name` attribute SHALL be omitted
- **AND** no error SHALL be recorded for the extraction failure
