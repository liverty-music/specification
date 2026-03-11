### Requirement: Watermill logs use structured JSON output
The backend SHALL output Watermill logs as structured JSON using Watermill's official slog adapter (`watermill.NewSlogLogger`). All Watermill log entries MUST include a `severity` field that GCP Cloud Logging can parse from `jsonPayload`.

#### Scenario: Watermill log appears as jsonPayload in GCP
- **WHEN** Watermill emits a log message (e.g., "Starting handler", "Subscriber stopped")
- **THEN** GCP Cloud Logging receives the log as `jsonPayload` with correct `severity` field matching the original log level

#### Scenario: Watermill INFO log is not classified as ERROR
- **WHEN** Watermill emits an INFO-level log
- **THEN** GCP Cloud Logging classifies the entry as severity `INFO`, not `ERROR`

### Requirement: Watermill and application logs share the same slog handler
The Watermill logger SHALL be derived from the application's `*logging.Logger` via `logger.Slog()`. Both loggers MUST use the same format, level, and output destination.

#### Scenario: Consistent log format between application and Watermill
- **WHEN** the application logger is configured with JSON format
- **THEN** Watermill logs also appear in JSON format with the same handler configuration
