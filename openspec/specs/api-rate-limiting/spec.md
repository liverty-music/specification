# API Rate Limiting

## Purpose

TBD — This capability defines rate limiting requirements for Connect-RPC endpoints, covering per-user and per-IP token bucket enforcement, interceptor placement, memory management, and configuration.

## Requirements

### Requirement: Per-user rate limiting for authenticated endpoints

The system SHALL enforce per-user rate limiting on all authenticated Connect-RPC endpoints using a token bucket algorithm keyed on the JWT `sub` claim.

#### Scenario: Authenticated user within rate limit

- **WHEN** an authenticated user sends requests within the configured rate limit (default: 100 req/sec, burst 200)
- **THEN** all requests SHALL be processed normally

#### Scenario: Authenticated user exceeds rate limit

- **WHEN** an authenticated user exceeds the configured rate limit
- **THEN** the system SHALL return `connect.CodeResourceExhausted`
- **AND** the response SHALL include a `Retry-After` header

#### Scenario: Different users have independent rate limits

- **WHEN** user A exceeds their rate limit
- **THEN** user B's requests SHALL NOT be affected

### Requirement: Per-IP rate limiting for unauthenticated endpoints

The system SHALL enforce per-IP rate limiting on public (unauthenticated) Connect-RPC endpoints using a token bucket algorithm keyed on client IP address.

#### Scenario: Anonymous client within rate limit

- **WHEN** an unauthenticated client sends requests to public endpoints within the configured rate limit (default: 30 req/sec, burst 60)
- **THEN** all requests SHALL be processed normally

#### Scenario: Anonymous client exceeds rate limit

- **WHEN** an unauthenticated client exceeds the configured rate limit for public endpoints
- **THEN** the system SHALL return `connect.CodeResourceExhausted`

#### Scenario: IP extraction from X-Forwarded-For

- **WHEN** the request contains an `X-Forwarded-For` header (from GKE Ingress/load balancer)
- **THEN** the system SHALL use the **rightmost** IP entry appended by the trusted GCP load balancer
- **AND** SHALL NOT use the leftmost entry, which is client-supplied and trivially spoofable
- **AND** SHALL fall back to `X-Real-Ip`, then an empty string if the header is absent

### Requirement: Rate limiter interceptor placement

The rate limit interceptor SHALL be placed in the Connect-RPC interceptor chain after the tracing interceptor and before the access log interceptor.

#### Scenario: Rate-limited request is traced and logged

- **WHEN** a request is rejected by the rate limiter
- **THEN** the rejection SHALL appear in the OpenTelemetry trace span
- **AND** the access log SHALL record the `ResourceExhausted` status

#### Scenario: Health check endpoints are exempt

- **WHEN** Kubernetes sends a health probe request
- **THEN** the rate limiter SHALL NOT apply to health check endpoints

### Requirement: Rate limiter memory management

The system SHALL evict idle rate limiter entries to prevent unbounded memory growth.

#### Scenario: Idle limiter eviction

- **WHEN** a rate limiter entry has not been accessed for 10 minutes
- **THEN** the system SHALL remove the entry from memory

#### Scenario: Evicted user resumes activity

- **WHEN** an evicted user sends a new request
- **THEN** a fresh rate limiter SHALL be created with full burst capacity

### Requirement: Rate limit configuration via environment variables

Rate limit parameters SHALL be configurable via environment variables.

#### Scenario: Custom authenticated rate limit

- **WHEN** `RATE_LIMIT_AUTH_RPS` is set to `50` and `RATE_LIMIT_AUTH_BURST` is set to `100`
- **THEN** authenticated users SHALL be limited to 50 requests per second with a burst of 100

#### Scenario: Default values when not configured

- **WHEN** rate limit environment variables are not set
- **THEN** the system SHALL use defaults: authenticated 100 rps / 200 burst, unauthenticated 30 rps / 60 burst
