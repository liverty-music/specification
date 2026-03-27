## 1. SDK Foundation (otel-sdk-configuration)

- [x] 1.1 Add `SamplerRatio float64` field to `TelemetryConfig` with envconfig tag `TELEMETRY_SAMPLER_RATIO` and default `1.0`
- [x] 1.2 Expand `SetupTelemetry` to accept `environment string` parameter and add `deployment.environment` resource attribute
- [x] 1.3 Replace `trace.AlwaysSample()` with `trace.ParentBased(trace.TraceIDRatioBased(ratio))`
- [x] 1.4 Add `otel.SetTextMapPropagator(propagation.TraceContext{})` call in setup
- [x] 1.5 Initialize MeterProvider with OTLP HTTP metric exporter (conditional on OTLPEndpoint), set global via `otel.SetMeterProvider()`
- [x] 1.6 Update `tracerCloser` to also shut down MeterProvider (rename to `telemetryCloser`)
- [x] 1.7 Update all `SetupTelemetry` call sites in DI (provider.go, consumer.go, job.go, image_sync_job.go) to pass environment
- [x] 1.8 Add unit tests for sampler ratio configuration and resource attribute construction

## 2. External HTTP Client Instrumentation (backend-otel-instrumentation)

- [x] 2.1 Add `go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp` dependency
- [x] 2.2 Create otelhttp-wrapped `*http.Client` in DI provider.go for Gemini clients using `UseDefaultCredentials()` pattern
- [x] 2.3 Create otelhttp-wrapped `*http.Client` in DI consumer.go for Google Maps (chain: otelhttp → RetryTransport)
- [x] 2.4 Create otelhttp-wrapped `*http.Client` in DI provider.go for Last.fm client (replace `nil`)
- [x] 2.5 Create otelhttp-wrapped `*http.Client` in DI provider.go for MusicBrainz client (replace `nil`)
- [x] 2.6 Create otelhttp-wrapped `*http.Client` in DI provider.go and consumer.go for fanart.tv client and LogoFetcher (replace `nil`)
- [x] 2.7 Add `go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc` dependency and wire `otelgrpc.NewClientHandler()` into Zitadel client via gRPC dial options

## 3. UseCase Spans (backend-otel-instrumentation)

- [x] 3.1 Add span in `BuildMerkleTree()` wrapping identity commitment computation and tree construction, with `merkle.leaf_count` attribute
- [x] 3.2 Add span in `executeSearch()` wrapping `FilterNew` deduplication, with `filter.scraped_count` and `filter.new_count` attributes
- [x] 3.3 Add span in `persistArtists()` wrapping the multi-pass dedup/merge logic, with `persist.input_count` and `persist.created_count` attributes

## 4. DB Semantic Convention Enrichment (db-trace-correlation)

- [x] 4.1 Extend `ExtractOperation()` to also return table name (regex for FROM/INTO/UPDATE patterns), rename to `ExtractQueryMeta()`
- [x] 4.2 Add `dbNamespace` and `serverAddress` fields to `TracedPool` and `TracedTx`, set from `DatabaseConfig` at construction
- [x] 4.3 Add `db.collection.name`, `db.namespace`, `server.address` attributes to `startSpan()` in TracedPool and TracedTx
- [x] 4.4 Extract `*pgconn.PgError` code in `recordError()` and set `db.response.status_code` attribute
- [x] 4.5 Update TracedPool/TracedTx constructor call sites in DI to pass database name and host
- [x] 4.6 Update existing unit tests for `ExtractQueryMeta()` and add test cases for table name extraction

## 5. Application Metrics (backend-otel-instrumentation)

- [x] 5.1 Add `go.opentelemetry.io/otel/sdk/metric` and `go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetrichttp` dependencies
- [x] 5.2 Create `blockchain.mint.duration` histogram and `blockchain.mint.total` counter in TicketUseCase, record on mint completion
- [x] 5.3 Register `db.pool.active_connections` and `db.pool.idle_connections` as ObservableGauges reading from `pgxpool.Pool.Stat()`

## 6. Context Propagation Fix (backend-otel-instrumentation)

- [x] 6.1 Replace `context.Background()` with `context.WithoutCancel(ctx)` in `markSearchCompleted()` and `markSearchFailed()` in concert_uc.go
