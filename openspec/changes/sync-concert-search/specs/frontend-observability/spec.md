## MODIFIED Requirements

### Requirement: ILogger OpenTelemetry Sink
The system SHALL provide a custom `ISink` implementation that bridges Aurelia 2's `ILogger` to OpenTelemetry spans.

#### Scenario: Multiple sinks are registered
- **WHEN** the application is configured
- **THEN** `LoggerConfiguration` SHALL register both `ConsoleSink` and `OtelLogSink`
- **AND** all log events SHALL be emitted to both sinks
- **AND** the log level SHALL be determined by the `VITE_LOG_LEVEL` environment variable
- **AND** the Dockerfile SHALL NOT set `ENV VITE_LOG_LEVEL` to avoid overriding the `.env` file value with an empty string
