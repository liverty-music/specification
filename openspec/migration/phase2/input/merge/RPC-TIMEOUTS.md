<!-- merge_group: RPC-TIMEOUTS | target: components/adapter/fan/web/rpc/timeouts | members: 2 -->

<!-- member: frontend-network-timeouts | flags:  -->
### Requirement: Default RPC call timeout

Every Connect-RPC call issued through the frontend's shared main-thread transport SHALL be bounded by a default client-side deadline so that a hung or unresponsive backend fails within a known window instead of leaving the request pending indefinitely. The default deadline SHALL be applied uniformly to all frontend applications (fan-web, admin, organizer) that construct RPC clients from the shared transport, and SHALL NOT require per-call or per-method configuration at the call site.

This requirement scopes only to RPC calls made through the shared main-thread transport. RPC calls originating in the Service Worker (which has no access to the main-thread dependency-injected configuration) are out of scope for this requirement; the Service Worker's own network calls are bounded separately (see the Service-Worker requirements below).

#### Scenario: A hung request is bounded by the default deadline

- **WHEN** an RPC call is issued and the backend does not produce a response within the configured default timeout
- **THEN** the call SHALL be aborted client-side and SHALL reject with `Code.DeadlineExceeded`
- **AND** the aborted request SHALL surface through the existing error-handling path (it SHALL NOT be silently retried, consistent with the existing policy of not retrying `DeadlineExceeded`)

#### Scenario: A fast request completes normally

- **WHEN** an RPC call is issued and the backend responds within the configured default timeout
- **THEN** the response SHALL be returned to the caller unchanged
- **AND** no timeout-related error SHALL be raised

#### Scenario: The deadline spans the recovery path

- **WHEN** an RPC call triggers the auth silent-refresh retry and/or the transient-error (`Unavailable`) retry-with-backoff within a single call
- **THEN** the whole recovery sequence SHALL share the one call deadline
- **AND** the call SHALL still reject with `Code.DeadlineExceeded` once the deadline elapses, rather than extending the deadline per retry

<!-- member: frontend-network-timeouts | flags:  -->
### Requirement: RPC timeout value is runtime-configurable

The default RPC timeout value SHALL be sourced from the runtime configuration (`/config.json`) so that it can be tuned per environment without rebuilding the SPA bundle. When the runtime configuration does not specify a value, the system SHALL fall back to a built-in default of 10 seconds.

#### Scenario: Configuration supplies a valid timeout value

- **WHEN** `/config.json` provides a valid RPC timeout value (a positive number) at bootstrap
- **THEN** the shared transport SHALL apply that value as the default RPC deadline

#### Scenario: Configuration omits the timeout value

- **WHEN** `/config.json` does not include an RPC timeout value
- **THEN** the shared transport SHALL apply the built-in default of 10 seconds
- **AND** bootstrap SHALL succeed without error

#### Scenario: Configuration supplies an invalid timeout value

- **WHEN** `/config.json` includes an RPC timeout value that is not a positive number (e.g. zero, negative, or non-numeric)
- **THEN** the invalid value SHALL be rejected and the shared transport SHALL apply the built-in default of 10 seconds
- **AND** bootstrap SHALL succeed without error

