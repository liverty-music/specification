# Database Trace Correlation

## Purpose

Defines the requirements for end-to-end trace correlation between backend application spans and Cloud SQL Query Insights execution-plan spans, using OTel span creation and sqlcommenter traceparent injection at the database query layer.

## ADDED Requirements

### Requirement: OTel span creation for database queries
The system SHALL create an OpenTelemetry child span for every database query executed through the connection pool, capturing the SQL operation, query text, and execution duration.

#### Scenario: SELECT query creates a client span
- **WHEN** a repository method executes a SELECT query via the pool wrapper
- **THEN** an OTel span SHALL be created with kind `Client`
- **AND** the span name SHALL be the SQL operation name (e.g., `SELECT`)
- **AND** the span SHALL have attribute `db.system` set to `postgresql`
- **AND** the span SHALL have attribute `db.query.text` set to the original SQL text (without injected comments)
- **AND** the span SHALL have attribute `db.operation.name` set to the extracted operation

#### Scenario: INSERT query creates a client span
- **WHEN** a repository method executes an INSERT query via the pool wrapper
- **THEN** an OTel span SHALL be created with span name `INSERT`
- **AND** the span SHALL record the duration of the query execution

#### Scenario: Query execution error is recorded on the span
- **WHEN** a database query fails with an error
- **THEN** the span SHALL record the error
- **AND** the span status SHALL be set to `Error`

---

### Requirement: sqlcommenter traceparent injection
The system SHALL inject a `traceparent` comment in sqlcommenter format into every SQL query, enabling Cloud SQL Query Insights to correlate its execution-plan spans with the backend application trace.

#### Scenario: traceparent comment is prepended to SQL
- **WHEN** a query is executed through the pool wrapper with an active OTel span in the context
- **THEN** the SQL sent to PostgreSQL SHALL be prepended with a comment in the format `/*traceparent='00-{trace_id}-{span_id}-{flags}'*/`
- **AND** the trace_id SHALL be the 32-character hex trace ID from the current span context
- **AND** the span_id SHALL be the 16-character hex span ID from the current span context
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
- **THEN** the wrapper SHALL return a traced transaction that applies span creation and comment injection to queries executed within the transaction

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
