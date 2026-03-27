# OTel SDK Configuration

## Purpose

Defines the requirements for the OpenTelemetry SDK initialization in the backend service, covering TracerProvider, MeterProvider, resource attributes, sampler strategy, and propagator setup.

## ADDED Requirements

### Requirement: Environment-aware trace sampling
The system SHALL use a `ParentBased(TraceIDRatioBased)` sampler configured via the `TELEMETRY_SAMPLER_RATIO` environment variable, defaulting to `1.0` (sample all).

#### Scenario: Production uses ratio-based sampling
- **WHEN** `TELEMETRY_SAMPLER_RATIO` is set to `0.1`
- **THEN** the TracerProvider SHALL sample approximately 10% of new root traces
- **AND** child spans SHALL inherit the parent's sampling decision

#### Scenario: Development samples all traces
- **WHEN** `TELEMETRY_SAMPLER_RATIO` is not set or set to `1.0`
- **THEN** the TracerProvider SHALL sample 100% of traces (equivalent to `AlwaysSample()`)

---

### Requirement: Enriched resource attributes
The system SHALL configure the OTel Resource with `deployment.environment` in addition to the existing `service.name` and `service.version`.

#### Scenario: Resource includes deployment environment
- **WHEN** the telemetry SDK is initialized
- **THEN** the Resource SHALL include attribute `deployment.environment` derived from the `ENVIRONMENT` config value (e.g., `local`, `development`, `staging`, `production`)

---

### Requirement: Explicit text map propagator
The system SHALL explicitly configure `propagation.TraceContext{}` as the global text map propagator.

#### Scenario: W3C TraceContext propagator is set
- **WHEN** the telemetry SDK is initialized
- **THEN** `otel.SetTextMapPropagator(propagation.TraceContext{})` SHALL be called
- **AND** cross-service trace context propagation SHALL use W3C TraceContext format

---

### Requirement: MeterProvider initialization
The system SHALL initialize an OTel MeterProvider alongside the TracerProvider, sharing the same Resource and OTLP endpoint.

#### Scenario: MeterProvider exports metrics via OTLP
- **WHEN** `TELEMETRY_OTLP_ENDPOINT` is configured
- **THEN** the MeterProvider SHALL be created with an OTLP HTTP metric exporter targeting the same endpoint
- **AND** the MeterProvider SHALL use the same Resource as the TracerProvider
- **AND** the global MeterProvider SHALL be set via `otel.SetMeterProvider()`

#### Scenario: MeterProvider is created without exporter when endpoint is not configured
- **WHEN** `TELEMETRY_OTLP_ENDPOINT` is not configured
- **THEN** the MeterProvider SHALL be created without an exporter (metrics recorded but not exported)

#### Scenario: MeterProvider is shut down during graceful shutdown
- **WHEN** the application receives a shutdown signal
- **THEN** the MeterProvider SHALL be shut down in the Observe phase alongside the TracerProvider
- **AND** pending metric data SHALL be flushed before shutdown completes
