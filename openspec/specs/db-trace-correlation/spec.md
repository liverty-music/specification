# Database Trace Correlation

## Purpose

Defines the requirements for end-to-end trace correlation between backend application spans and Cloud SQL Query Insights execution-plan spans, using OTel span creation and sqlcommenter traceparent injection at the database query layer.

## Requirements

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

---

### Requirement: sqlcommenter traceparent injection
The system SHALL inject a `traceparent` comment in sqlcommenter format into every SQL query, enabling Cloud SQL Query Insights to correlate its execution-plan spans with the backend application trace.

#### Scenario: traceparent comment is prepended to SQL
- **WHEN** a query is executed through the pool wrapper with an active OTel span in the context
- **THEN** the SQL sent to PostgreSQL SHALL be prepended with a comment in the format `/*traceparent='00-{trace_id}-{span_id}-{flags}'*/`
- **AND** the trace_id SHALL be the 32-character hex trace ID from the current span context
- **AND** the span_id SHALL be the 16-character hex span ID of the DB query span created by the wrapper (not the caller's incoming span)
- **AND** the flags SHALL be the 2-character hex trace flags from the current span context

#### Scenario: No comment injection when no active span
- **WHEN** a query is executed through the pool wrapper without an active OTel span in the context
- **THEN** the SQL SHALL be sent to PostgreSQL unmodified (no comment prepended)

---

### Requirement: Transparent pool wrapping
The system SHALL wrap the `*pgxpool.Pool` with a `TracedPool` that is transparent to repository code — repositories SHALL NOT require any code changes to be instrumented.

#### Scenario: Repository uses pool wrapper without code changes
- **WHEN** a repository calls `Query`, `QueryRow`, or `Exec` on the pool
- **THEN** the call SHALL be intercepted by the wrapper for span creation and comment injection
- **AND** the call SHALL be delegated to the underlying `*pgxpool.Pool`
- **AND** the result SHALL be returned unmodified to the repository

#### Scenario: Pool wrapper supports Begin for transactions
- **WHEN** a repository calls `Begin` to start a transaction
- **THEN** an OTel span SHALL be created for the `Begin` call itself
- **AND** the wrapper SHALL return a traced transaction that applies span creation and comment injection to queries executed within the transaction

---

### Requirement: Transaction query tracing
The system SHALL trace individual queries executed within a database transaction, applying the same span creation and comment injection as direct pool queries.

#### Scenario: Query within transaction creates a span
- **WHEN** a query is executed via a transaction obtained from `Begin`
- **THEN** an OTel span SHALL be created for that query
- **AND** the SQL SHALL be prepended with the traceparent comment

#### Scenario: Commit and Rollback create spans
- **WHEN** a transaction is committed or rolled back
- **THEN** an OTel span SHALL be created for the Commit or Rollback operation
