# Frontend Observability

## MODIFIED Requirements

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
