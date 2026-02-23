# Interceptor Chain Ordering Capability

## Purpose

Defines the correct ordering of Connect-RPC interceptors in the backend server, ensuring that all logs include trace context, error responses use correct gRPC status codes, and panics do not bypass observability layers.

## Requirements

### Requirement: Interceptor Execution Order

The system SHALL register Connect interceptors in the following order (outermost to innermost): tracing, access log, error handling, panic recovery, claims bridge, validation.

**Rationale**: Each interceptor has data dependencies on other interceptors. The ordering MUST satisfy these constraints:
1. Tracing MUST be outermost so that all inner interceptors receive an OTel span in their `ctx` argument.
2. Access log MUST be outside error handling so it sees `*connect.Error` (not raw `AppErr`) for correct status codes.
3. Access log MUST be outside panic recovery so that its post-`next()` logging code is not bypassed by stack unwinding during panics.
4. Error handling MUST be outside panic recovery so that `*connect.Error` returned by the recover handler flows through normally.
5. Claims bridge MUST run after the HTTP-layer `authn.Middleware` has set `authn.infoKey` in the context (always satisfied since HTTP middleware runs before Connect interceptors).

#### Scenario: Normal request with application error

- **WHEN** a handler returns an `AppErr`
- **THEN** the error SHALL flow through the panic recovery interceptor unchanged
- **AND** the error handling interceptor SHALL convert it to a `*connect.Error` with the appropriate gRPC status code
- **AND** the access log interceptor SHALL log the request with the correct gRPC status code string (e.g., `"not_found"`, `"internal"`)
- **AND** the access log entry SHALL include `trace_id` and `span_id` from the OTel span
- **AND** the tracing interceptor SHALL record the span status using the converted `*connect.Error`

#### Scenario: Handler panic

- **WHEN** a handler panics during request processing
- **THEN** the panic recovery interceptor SHALL catch the panic via `defer recover()`
- **AND** the panic recovery interceptor SHALL log the panic with `trace_id` and `span_id` from the OTel span
- **AND** the panic recovery interceptor SHALL return `connect.CodeInternal` as a `*connect.Error`
- **AND** the error handling interceptor SHALL pass the `*connect.Error` through unchanged
- **AND** the access log interceptor SHALL log the request with status `"internal"`
- **AND** the access log entry SHALL include `trace_id` and `span_id`

#### Scenario: Validation failure

- **WHEN** a request fails protovalidate validation
- **THEN** the validation interceptor SHALL return `connect.CodeInvalidArgument` without calling the handler
- **AND** the error SHALL flow outward through claims bridge, panic recovery, error handling, and access log
- **AND** the access log SHALL record status `"invalid_argument"`

### Requirement: Interceptor Ordering Documentation

The system SHALL include inline code comments in the interceptor registration code that document the ordering rationale, the execution order, and the data dependency constraints.

**Rationale**: Interceptor ordering bugs are subtle and difficult to diagnose. Future maintainers MUST understand why each interceptor is at its specific position to avoid regressions.

#### Scenario: Developer modifies interceptor chain

- **WHEN** a developer reads the interceptor registration code
- **THEN** the code comments SHALL explain the execution order (outermost to innermost)
- **AND** the comments SHALL explain why each interceptor is at its specific position
- **AND** the comments SHALL describe the context propagation model (enriched `ctx` flows inward via function arguments)
