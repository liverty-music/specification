## MODIFIED Requirements

### Requirement: ILogger OpenTelemetry Sink
The system SHALL provide a custom `ISink` implementation that bridges Aurelia 2's `ILogger` to OpenTelemetry spans.

#### Scenario: Error-level log creates OTEL span
- **WHEN** a component or service calls `logger.error()` or `logger.fatal()`
- **THEN** the `OtelLogSink` SHALL create an OTEL span with the log message
- **AND** the span SHALL include attributes: `log.scope` (the logger's scope name), `log.severity`, and any additional log data
- **AND** if the log includes an Error object, the sink SHALL call `span.recordException()`

#### Scenario: Non-error logs are ignored by OTEL sink
- **WHEN** a component or service calls `logger.info()`, `logger.debug()`, `logger.warn()`, or `logger.trace()`
- **THEN** the `OtelLogSink` SHALL NOT create an OTEL span
- **AND** these logs SHALL still be handled by the `ConsoleSink`

#### Scenario: Multiple sinks are registered
- **WHEN** the application is configured
- **THEN** `LoggerConfiguration` SHALL register both `ConsoleSink` and `OtelLogSink`
- **AND** all log events SHALL be emitted to both sinks
- **AND** the log level SHALL be determined by the `VITE_LOG_LEVEL` environment variable

#### Scenario: Log level controlled by environment variable
- **WHEN** `VITE_LOG_LEVEL` is set to a valid level (trace, debug, info, warn, error)
- **THEN** the `LoggerConfiguration` level SHALL match the specified level

#### Scenario: Log level fallback when unset in development
- **WHEN** `VITE_LOG_LEVEL` is not set
- **AND** the build mode is development (`import.meta.env.DEV === true`)
- **THEN** the `LoggerConfiguration` level SHALL be `LogLevel.debug`

#### Scenario: Log level fallback when unset in production
- **WHEN** `VITE_LOG_LEVEL` is not set
- **AND** the build mode is production (`import.meta.env.DEV === false`)
- **THEN** the `LoggerConfiguration` level SHALL be `LogLevel.warn`
