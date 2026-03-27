# Backend OTel Instrumentation

## Purpose

Defines the requirements for tracing external HTTP/gRPC client calls, adding UseCase-level spans for CPU-intensive business logic, and introducing application-level metrics in the backend service.

## ADDED Requirements

### Requirement: External HTTP client tracing via otelhttp transport
The system SHALL instrument all outbound HTTP clients with `otelhttp.NewTransport()` at the DI layer, creating automatic spans for every HTTP request with standard attributes (method, URL, status code, duration).

#### Scenario: Gemini API call creates an HTTP client span
- **WHEN** the ConcertSearcher calls the Gemini Vertex AI API
- **THEN** an OTel span SHALL be created with kind `Client`
- **AND** the span SHALL have standard HTTP attributes (`http.request.method`, `url.full`, `http.response.status_code`)
- **AND** the Gemini client SHALL use `ClientConfig.UseDefaultCredentials()` to layer ADC authentication on top of the otelhttp-wrapped transport
- **AND** the otelhttp span SHALL NOT contain authorization headers in its attributes

#### Scenario: Google Maps Places API call creates an HTTP client span
- **WHEN** the Google Maps client calls the Places API
- **THEN** an OTel span SHALL be created with kind `Client`
- **AND** the existing `RetryTransport` SHALL be chained after `otelhttp.NewTransport()` (otelhttp outermost)

#### Scenario: Last.fm API call creates an HTTP client span
- **WHEN** the Last.fm client makes an API request
- **THEN** an OTel span SHALL be created with kind `Client`
- **AND** the span SHALL capture the full request duration including any throttle wait time

#### Scenario: MusicBrainz API call creates an HTTP client span
- **WHEN** the MusicBrainz client makes an API request
- **THEN** an OTel span SHALL be created with kind `Client`

#### Scenario: fanart.tv API call creates an HTTP client span
- **WHEN** the fanart.tv client or LogoFetcher makes an HTTP request
- **THEN** an OTel span SHALL be created with kind `Client`

---

### Requirement: Zitadel gRPC client tracing via otelgrpc
The system SHALL instrument the Zitadel gRPC client with `otelgrpc` stats handler, creating automatic spans for every gRPC call.

#### Scenario: Zitadel email verification call creates a gRPC client span
- **WHEN** the EmailVerifier sends a verification email via the Zitadel gRPC API
- **THEN** an OTel span SHALL be created with kind `Client`
- **AND** the span SHALL have standard RPC attributes (`rpc.system`, `rpc.method`, `rpc.grpc.status_code`)

---

### Requirement: UseCase spans for CPU-intensive business logic
The system SHALL create OTel spans for in-process operations where CPU-bound computation is the primary time cost, limited to methods where external API and DB spans do not cover the processing time.

#### Scenario: Merkle tree construction creates a span
- **WHEN** `BuildMerkleTree()` computes identity commitments and constructs the Merkle tree
- **THEN** an OTel span SHALL be created with name `BuildMerkleTree`
- **AND** the span SHALL have attribute `merkle.leaf_count` set to the number of tickets processed

#### Scenario: Concert deduplication creates a span
- **WHEN** `executeSearch()` calls `FilterNew` to deduplicate scraped concerts against existing ones
- **THEN** an OTel span SHALL be created with name `FilterNewConcerts`
- **AND** the span SHALL have attributes `filter.scraped_count` and `filter.new_count`

#### Scenario: Artist batch persistence creates a span
- **WHEN** `persistArtists()` performs the multi-pass deduplication and merge operation
- **THEN** an OTel span SHALL be created with name `PersistArtists`
- **AND** the span SHALL have attributes `persist.input_count` and `persist.created_count`

---

### Requirement: Application metrics
The system SHALL expose application-level metrics via the OTel Metrics API, exported through OTLP to the OTel Collector.

#### Scenario: External API call duration is recorded as a histogram
- **WHEN** an external HTTP client completes a request
- **THEN** `otelhttp` SHALL automatically record `http.client.request.duration` histogram
- **AND** the metric SHALL include attributes for the target service name and response status

#### Scenario: Blockchain mint operations record duration and count
- **WHEN** a ticket mint operation completes (success or failure)
- **THEN** the system SHALL record `blockchain.mint.duration` histogram with the total duration including retries
- **AND** the system SHALL increment `blockchain.mint.total` counter with attribute `outcome` (success, retry_exhausted, error)

#### Scenario: Database connection pool gauges are observable
- **WHEN** the metrics export interval fires
- **THEN** the system SHALL report `db.pool.active_connections` gauge from `pgxpool.Pool.Stat().AcquiredConns()`
- **AND** the system SHALL report `db.pool.idle_connections` gauge from `pgxpool.Pool.Stat().IdleConns()`

---

### Requirement: Trace context preservation in deferred operations
The system SHALL preserve trace context when executing deferred status updates that must outlive the parent request's cancellation.

#### Scenario: Concert search status update preserves trace context
- **WHEN** `markSearchCompleted()` or `markSearchFailed()` runs after the search completes or times out
- **THEN** the function SHALL use `context.WithoutCancel(ctx)` instead of `context.Background()`
- **AND** the resulting DB span SHALL be a child of the original search trace
- **AND** the cancellation signal from the parent context SHALL NOT propagate to the status update
