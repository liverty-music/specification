# frontend-network-timeouts Specification

## Purpose
Defines the client-side network timeout policy for the Aurelia 2 frontend: a bounded default deadline for every Connect-RPC call and bounded Service-Worker `fetch()` calls, so that no browser-originated network request can hang without an upper bound and stalled requests fail closed with predictable behavior.
## Requirements
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

### Requirement: Service-Worker analytics capture is time-bounded

The Service-Worker `fetch()` that delivers a notification-interaction event to the analytics endpoint SHALL be bounded by a timeout, so that a slow (not failed) response is converted into an abort and routed through the existing offline-resend path rather than being lost or holding the Service Worker active.

#### Scenario: A slow analytics capture is stashed for resend

- **WHEN** the analytics capture `fetch()` does not complete within its timeout
- **THEN** the fetch SHALL be aborted
- **AND** the interaction SHALL be treated as a failed send and stashed for retry via the existing Background-Sync / app-open resend path
- **AND** the same de-duplication identifier SHALL be reused so the eventual resend is not double-counted

### Requirement: Service-Worker VAPID key fetch is time-bounded

The Service-Worker cache-miss `fetch()` that reads the VAPID public key from `/config.json` during push-subscription renewal SHALL be bounded by a timeout, so that a `pushsubscriptionchange` handler cannot hang on a stalled network fetch.

#### Scenario: A stalled VAPID fetch does not hang renewal

- **WHEN** the VAPID key is not present in the cache and the network `fetch()` for `/config.json` does not complete within its timeout
- **THEN** the fetch SHALL be aborted
- **AND** the renewal SHALL treat the key as unavailable and skip renewal without throwing
- **AND** the existing app-open reconciliation path SHALL remain able to recover the subscription on next app launch

This scenario bounds only the VAPID-key `fetch()`; it does not change how the Service Worker treats an existing or stale subscription endpoint (that behavior remains governed by the `push-notification-service` capability).

