## Why

The backend currently instruments only the RPC entry layer (otelconnect) and database queries (TracedPool), leaving the entire business logic layer and all external API calls as blind spots. When a request takes 5 seconds but DB queries account for only 50ms, there is no visibility into where the remaining time is spent. Additionally, the Metrics signal is completely absent, and the SDK configuration uses `AlwaysSample()` which is unsuitable for production traffic.

## What Changes

- Instrument all external HTTP clients (Gemini, Google Places, Last.fm, MusicBrainz, fanart.tv, Logo Fetcher) with `otelhttp.NewTransport()` and the Zitadel gRPC client with `otelgrpc`
- Add UseCase-level spans for CPU-intensive in-process logic: Merkle tree construction, concert deduplication, and artist batch persistence
- Introduce the Metrics signal: MeterProvider initialization, RPC/external API histograms, blockchain operation counters, and DB pool gauges
- Enhance the OTel SDK setup: environment-aware sampler, additional resource attributes (`deployment.environment`), explicit `TextMapPropagator`, and `SpanLimits`
- Enrich DB spans with missing Semantic Convention attributes: `db.collection.name`, `db.namespace`, `server.address`, `db.response.status_code`
- Fix trace context loss in `ConcertUseCase` where `context.Background()` severs parent traces for search status updates

## Capabilities

### New Capabilities

- `backend-otel-instrumentation`: Covers external HTTP/gRPC client tracing, UseCase-level span placement, and Metrics signal introduction for the backend service
- `otel-sdk-configuration`: Covers OTel SDK initialization enhancements including sampler strategy, resource attributes, propagator setup, MeterProvider, and span limits

### Modified Capabilities

- `db-trace-correlation`: Add missing DB Semantic Convention attributes (`db.collection.name`, `db.namespace`, `server.address`, `db.response.status_code`) to TracedPool and TracedTx spans

## Impact

- **backend repo**: `pkg/telemetry/`, `internal/infrastructure/` (all external clients), `internal/usecase/` (3 methods), `internal/infrastructure/database/rdb/` (TracedPool/TracedTx), `internal/di/` (DI wiring for instrumented clients)
- **Dependencies**: Add `go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp`, `go.opentelemetry.io/otel/sdk/metric`, `go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetrichttp`, `go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc`
- **Config**: New environment variable for sampler ratio (e.g., `TELEMETRY_SAMPLER_RATIO`); `deployment.environment` resource attribute derived from existing config
- **OTel Collector**: Needs metrics pipeline added (OTLP metrics receiver → Cloud Monitoring exporter) — out of scope for this change but a prerequisite for metrics visibility
