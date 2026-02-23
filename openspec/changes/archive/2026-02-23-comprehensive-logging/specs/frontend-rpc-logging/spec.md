## ADDED Requirements

### Requirement: Connect-RPC Logging Interceptor
The system SHALL provide a transport interceptor that logs all Connect-RPC requests and responses using Aurelia 2's ILogger.

#### Scenario: RPC request start is logged
- **WHEN** a Connect-RPC request is initiated
- **THEN** the system SHALL log at DEBUG level with message "RPC request"
- **AND** the log SHALL include the RPC method name

#### Scenario: Successful RPC response is logged
- **WHEN** a Connect-RPC request completes successfully
- **THEN** the system SHALL log at DEBUG level with message "RPC response"
- **AND** the log SHALL include the RPC method name and duration in milliseconds

#### Scenario: Failed RPC response is logged
- **WHEN** a Connect-RPC request fails with a ConnectError
- **THEN** the system SHALL log at ERROR level with message "RPC error"
- **AND** the log SHALL include the RPC method name, duration in milliseconds, and Connect error code

#### Scenario: Interceptor is registered in transport chain
- **WHEN** the Connect-RPC transport is created
- **THEN** the logging interceptor SHALL be registered in the interceptor chain alongside the existing OTEL and auth interceptors

---

### Requirement: Structured Logger Usage in Transport Layer
The system SHALL use Aurelia 2's ILogger instead of console.* for all logging in the transport layer.

#### Scenario: Auth interceptor error uses structured logger
- **WHEN** the auth interceptor fails to get a user from UserManager
- **THEN** the system SHALL log the error using `ILogger.error()` scoped to the transport
- **AND** the system SHALL NOT use `console.error()`

#### Scenario: Service Worker registration failure uses structured logger
- **WHEN** Service Worker registration fails during application startup
- **THEN** the system SHALL log the failure using `ILogger.warn()`
- **AND** the system SHALL NOT use `console.warn()`

---

### Requirement: ZK Proof Generation Timing Metrics
The system SHALL log timing metrics for ZK proof generation to enable performance analysis.

#### Scenario: Proof generation duration is logged
- **WHEN** a ZK proof generation completes (success or failure)
- **THEN** the system SHALL log at INFO level with message "proof generation complete"
- **AND** the log SHALL include `durationMs` (total time from start to finish)

#### Scenario: Proof generation failure is logged
- **WHEN** a ZK proof generation fails
- **THEN** the system SHALL log at ERROR level with the error details and `durationMs`
