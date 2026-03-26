## ADDED Requirements

### Requirement: Gemini client-cancelled errors classified as client error

The Gemini infrastructure layer SHALL classify HTTP 499 (Client Cancelled) responses as `codes.Canceled` instead of `codes.Unknown`. This ensures the error handling interceptor treats it as a client error and does not log it at ERROR level.

#### Scenario: Gemini API returns HTTP 499

- **WHEN** the Gemini API returns HTTP status 499 (Client Cancelled)
- **THEN** the error SHALL be classified as `codes.Canceled` (client error)
- **AND** the error handling interceptor SHALL NOT log it at ERROR level

#### Scenario: Server-side deadline exceeded is still logged

- **WHEN** the server's handler timeout expires (context.DeadlineExceeded)
- **THEN** the error SHALL continue to be logged at ERROR level
- **AND** the error SHALL be classified as `codes.DeadlineExceeded` (server error)

### Requirement: Infrastructure layer preserves original error types

The database infrastructure layer (`rdb.toAppErr`) SHALL NOT wrap unknown errors as `codes.Internal` AppErr. For errors that do not match any known database error pattern (pgx, pgconn), the layer SHALL wrap the error with `fmt.Errorf` to add context while preserving the original error chain.

This ensures that usecase and interceptor layers can inspect the original error type using `errors.Is` and `errors.As`.

#### Scenario: context.Canceled from database query

- **WHEN** a database query returns `context.Canceled`
- **THEN** `rdb.toAppErr` SHALL wrap it with `fmt.Errorf` preserving the original error
- **AND** `errors.Is(err, context.Canceled)` on the wrapped error SHALL return true

#### Scenario: Known pgx error is still mapped to AppErr

- **WHEN** a database query returns `pgx.ErrNoRows`
- **THEN** `rdb.toAppErr` SHALL wrap it as `codes.NotFound` AppErr (unchanged behavior)

#### Scenario: PostgreSQL constraint violation is still mapped to AppErr

- **WHEN** a database query returns a PostgreSQL unique violation (23505)
- **THEN** `rdb.toAppErr` SHALL wrap it as `codes.AlreadyExists` AppErr (unchanged behavior)

### Requirement: Standard slog output uses structured JSON format

All log output from the Go standard `slog` package SHALL use the application's configured structured logging format (JSON) by setting `slog.SetDefault()` after logger initialization.

This prevents the GKE logging agent from misclassifying INFO/WARN logs written to stderr as ERROR severity.

#### Scenario: NATS connection retry logged as INFO/WARN

- **WHEN** the NATS client retries a connection during startup
- **AND** the retry log is emitted via the standard `slog` package
- **THEN** the log entry SHALL be written in JSON format with the correct `severity` field
- **AND** GKE Cloud Logging SHALL classify it according to the `severity` field (INFO or WARN), not as ERROR

#### Scenario: NATS connection established after retry

- **WHEN** the NATS client successfully connects after retries
- **AND** emits an INFO log via the standard `slog` package
- **THEN** the log entry SHALL appear as `severity=INFO` in Cloud Logging (not ERROR)
