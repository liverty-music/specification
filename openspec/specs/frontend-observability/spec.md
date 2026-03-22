# Frontend Observability

## Purpose

Defines the OpenTelemetry-based observability infrastructure for the Aurelia 2 frontend, enabling distributed tracing from browser to Go backend, Connect-RPC error instrumentation, and bridging Aurelia's ILogger to OTEL spans.

## Requirements

### Requirement: OpenTelemetry Browser SDK Integration
The system SHALL integrate OpenTelemetry browser SDK for distributed tracing, enabling request correlation between the frontend and Go backend via W3C Trace Context headers. The frontend SHALL NOT export spans to an external collector.

#### Scenario: OTEL tracer provider is initialized at startup
- **WHEN** the Aurelia 2 application starts
- **THEN** the system SHALL initialize a `WebTracerProvider` without any span exporters
- **AND** the system SHALL register the provider as the global tracer provider

#### Scenario: Fetch requests include trace context headers
- **WHEN** the browser makes a fetch request to the backend API domain
- **THEN** the `instrumentation-fetch` package SHALL automatically inject `traceparent` and `tracestate` headers (W3C Trace Context)
- **AND** the backend SHALL use these headers to continue the distributed trace
- **AND** `propagateTraceHeaderCorsUrls` SHALL be configured to match the backend API origin

#### Scenario: Non-API requests are not instrumented
- **WHEN** the browser makes a fetch request to a third-party domain (e.g., Last.fm API, Zitadel)
- **THEN** the system SHALL NOT inject trace context headers into that request

#### Scenario: No spans are exported from the browser
- **WHEN** the tracer provider is initialized
- **THEN** no `BatchSpanProcessor` with an `OTLPTraceExporter` SHALL be configured
- **AND** the `VITE_OTEL_EXPORTER_URL` environment variable SHALL NOT be required

---

### Requirement: Connect-RPC Error Instrumentation
The system SHALL capture Connect-RPC error details as OpenTelemetry span attributes via a transport interceptor.

#### Scenario: Successful RPC call creates span
- **WHEN** a Connect-RPC call completes successfully
- **THEN** the system SHALL create an OTEL span with name `rpc/{method-name}`
- **AND** the span SHALL include attributes: `rpc.system=connect`, `rpc.service`, `rpc.method`
- **AND** the span status SHALL be set to `OK`

#### Scenario: Failed RPC call records error on span
- **WHEN** a Connect-RPC call fails with a `ConnectError`
- **THEN** the system SHALL set the span status to `ERROR` with the error message
- **AND** the span SHALL include attribute `rpc.connect.error_code` with the Connect error code
- **AND** the system SHALL call `span.recordException()` with the error

#### Scenario: RPC error context is forwarded to ErrorBoundaryService
- **WHEN** a Connect-RPC call fails and the caller does not handle the error
- **THEN** the error SHALL propagate to the global error handler
- **AND** the `ErrorBoundaryService` SHALL capture the error with RPC context (service name, method name, error code)

---

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
