## Purpose

Give operators an automatic signal when backend goroutines become permanently blocked on concurrency primitives, so silent consumer or RPC wedges are detected and alerted instead of surfacing later as a user-reported outage.

## ADDED Requirements

### Requirement: Goroutine leak profile is exposed

The backend SHALL expose a goroutine leak profile that reports goroutines detected as permanently blocked on a concurrency primitive (channel operation, `sync.Mutex`, or `sync.Cond`) with no possibility of becoming runnable. The profile SHALL be retrievable at runtime from a running backend instance without a restart or redeploy, and each entry SHALL include the blocked goroutine's stack so the blocking site can be identified.

#### Scenario: Profile retrievable from a healthy instance

- **WHEN** an operator requests the goroutine leak profile from a running backend instance that has no leaked goroutines
- **THEN** the request succeeds and returns an empty (zero-entry) profile

#### Scenario: Leaked goroutine appears in the profile with its stack

- **WHEN** a goroutine is permanently blocked on a channel receive, mutex, or condition variable that can never unblock, and an operator requests the goroutine leak profile
- **THEN** the profile includes an entry for that goroutine annotated with its blocking stack trace

#### Scenario: Profiling endpoint is not publicly reachable

- **WHEN** the goroutine leak profiling endpoint is deployed
- **THEN** it is reachable only through operator/internal access paths and is not exposed on a public, unauthenticated route

### Requirement: Detected goroutine leaks raise an alert

The backend's monitoring SHALL raise an alert to the operations notification channel when the goroutine leak profile reports one or more leaked goroutines that persist beyond a transient window, so that a silent wedge is escalated without depending on a user report. The alert SHALL identify the affected workload.

#### Scenario: Sustained leak escalates to operators

- **WHEN** the goroutine leak profile reports one or more leaked goroutines on a workload continuously beyond the configured evaluation window
- **THEN** an alert is delivered to the operations notification channel identifying the affected workload

#### Scenario: Transient blocking does not alert

- **WHEN** a goroutine appears blocked only momentarily and clears within the evaluation window
- **THEN** no alert is raised

#### Scenario: Incident auto-resolves when leaks clear

- **WHEN** a previously alerting workload reports zero leaked goroutines for the configured recovery window
- **THEN** the corresponding incident is automatically closed

### Requirement: Leak detection complements existing consumer health signals

The goroutine leak alert SHALL be an additional, independent signal that does not replace existing consumer backlog-stall or liveness alerting, so that a wedge missed by backlog metrics is still caught, and its scope and known blind spots (leaks reachable only through global variables or through goroutines that remain runnable) SHALL be documented for operators.

#### Scenario: Wedge invisible to backlog metrics is still detected

- **WHEN** a consumer goroutine is wedged on a concurrency primitive while its backlog metric does not breach the backlog-stall threshold
- **THEN** the goroutine leak alert still fires for that workload independently of the backlog-stall alert

#### Scenario: Known blind spots are documented

- **WHEN** an operator consults the capability's documentation
- **THEN** it states that the profile may miss leaks reachable only via global variables or via still-runnable goroutines, and directs the operator to complementary signals for those cases
