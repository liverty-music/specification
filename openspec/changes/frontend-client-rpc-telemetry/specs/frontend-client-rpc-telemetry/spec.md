## Purpose

Defines client-side observability for the Aurelia 2 frontend's Connect-RPC calls: the frontend SHALL capture the distribution of client-observed RPC call durations (including the auth silent-refresh and transient-retry recovery tail that the client deadline bounds) and the rate at which the client-side deadline is exceeded, and report them as aggregates, so the default RPC timeout policy can be validated and tuned from production data rather than guessed.

## ADDED Requirements

### Requirement: Client-observed RPC duration is captured

Every Connect-RPC call issued through the frontend's shared main-thread transport SHALL contribute its **client-observed total duration** to an aggregated latency distribution. The measured duration SHALL span the entire client call as the user experiences it — including any auth silent-refresh retry and transient-error (`Unavailable`) retry-with-backoff that occur within that single call — so the recorded distribution reflects the same wall-clock window that the client-side default deadline bounds.

Each measurement SHALL be attributed to its terminal outcome, distinguishing at least: success, `DeadlineExceeded`, and other error codes. The distribution SHALL be retained as bucketed counts (a histogram), not as pre-computed percentiles, so that fleet-wide percentiles can be computed at query time.

#### Scenario: A completed call contributes its duration

- **WHEN** an RPC call issued through the shared transport terminates (successfully or with an error)
- **THEN** its client-observed total duration SHALL be added to the aggregated distribution under a latency bucket
- **AND** the measurement SHALL be attributed to the call's terminal outcome (success or specific error code)

#### Scenario: The recovery tail is included in the measured duration

- **WHEN** a call triggers the auth silent-refresh retry and/or the transient-`Unavailable` retry-with-backoff before terminating
- **THEN** the recorded duration SHALL cover the whole recovery sequence within that call, not just the final attempt

### Requirement: Deadline-exceeded rate is observable

The telemetry SHALL make the rate at which the client-side deadline fires observable. It SHALL record the count of calls terminating with `DeadlineExceeded` alongside the total count of calls in the same window, so that a deadline-firing rate can be derived without access to any individual request.

#### Scenario: A deadline-exceeded call is counted

- **WHEN** an RPC call is aborted by the client-side deadline and rejects with `DeadlineExceeded`
- **THEN** the deadline-exceeded count for the current window SHALL be incremented
- **AND** the total-call count for the same window SHALL also include it, so a rate can be computed

### Requirement: Telemetry is reported as aggregates, not per-request events

The telemetry SHALL be reported as a small number of **aggregate snapshots** per session (bucketed distribution counts plus per-outcome tallies for the window) rather than one report per RPC call. A single call SHALL NOT produce its own individual telemetry report.

#### Scenario: Many calls produce few telemetry reports

- **WHEN** many RPC calls complete within a reporting window
- **THEN** the telemetry SHALL emit at most a bounded number of aggregate reports for that window (independent of the number of calls)
- **AND** no per-call telemetry report SHALL be emitted

### Requirement: Pending telemetry is flushed at session end

Aggregated telemetry that has not yet been reported SHALL be flushed when the page is being hidden or unloaded, so that short sessions and the final window of a session are not lost.

#### Scenario: A short session still reports

- **WHEN** the page transitions to hidden/unloaded with unreported aggregated telemetry pending
- **THEN** the pending aggregate SHALL be flushed on that transition
- **AND** the report SHALL use a delivery mechanism that can survive the page being torn down

### Requirement: Telemetry honors analytics opt-out and unconfigured analytics

Client-side RPC telemetry SHALL be treated as analytics data: when the user has opted out of analytics, or when analytics is not configured for the environment, the telemetry SHALL be a strict no-op — nothing is collected for sending and no telemetry report is emitted. This mirrors the frontend's existing analytics nil-config / opt-out posture.

#### Scenario: Opted-out user sends no telemetry

- **WHEN** the user has opted out of analytics (or analytics is unconfigured)
- **THEN** no RPC-telemetry report SHALL be emitted
- **AND** the absence of telemetry SHALL NOT affect RPC behavior in any way

### Requirement: Telemetry carries no personally identifying request content

An RPC-telemetry report SHALL contain only non-identifying aggregate observability data — coarse latency buckets, terminal-outcome tallies, and the RPC method identity — and SHALL NOT include request or response payloads, arguments, tokens, or any personally identifying content.

#### Scenario: A report excludes request content

- **WHEN** an aggregate telemetry report is assembled
- **THEN** it SHALL include only latency-bucket counts, outcome tallies, and method identity
- **AND** it SHALL NOT include any request/response payload, credential, or personally identifying field
