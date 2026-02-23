## ADDED Requirements

### Requirement: Connect-RPC Request/Response Logging
The system SHALL log Connect-RPC request/response lifecycle via a dedicated logging interceptor, separate from the OTEL tracing interceptor.

#### Scenario: Logging interceptor coexists with OTEL interceptor
- **WHEN** the Connect-RPC transport is configured
- **THEN** the logging interceptor SHALL be registered alongside the existing OTEL interceptor
- **AND** both interceptors SHALL operate independently (logging interceptor writes to ILogger, OTEL interceptor writes to spans)
- **AND** the interceptor order SHALL be: OTEL, logging, auth
