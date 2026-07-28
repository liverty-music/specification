## MODIFIED Requirements

### Requirement: Error log detection per workload

The system SHALL detect ERROR-level log entries from each backend workload (server, consumer, concert-discovery, sales-phase-discovery, merch-discovery) independently using Cloud Monitoring Log-Based Alert Policies.

Each Alert Policy SHALL filter logs by:
- `resource.type = "k8s_container"`
- `resource.labels.namespace_name = "backend"`
- `labels.k8s-pod/app` matching the specific workload name
- `severity = "ERROR"`

#### Scenario: Server emits an ERROR log

- **WHEN** the server workload emits a log entry with severity ERROR
- **THEN** the server-specific Alert Policy detects the log entry and opens an Incident

#### Scenario: Consumer emits an ERROR log

- **WHEN** the consumer workload emits a log entry with severity ERROR
- **THEN** the consumer-specific Alert Policy detects the log entry and opens an Incident

#### Scenario: Concert-discovery CronJob emits an ERROR log

- **WHEN** the concert-discovery CronJob emits a log entry with severity ERROR
- **THEN** the concert-discovery-specific Alert Policy detects the log entry and opens an Incident

#### Scenario: Sales-phase-discovery CronJob emits an ERROR log

- **WHEN** the sales-phase-discovery CronJob emits a log entry with severity ERROR (for example, a startup database ping failure or a per-artist searcher failure)
- **THEN** the sales-phase-discovery-specific Alert Policy detects the log entry and opens an Incident

#### Scenario: Merch-discovery CronJob emits an ERROR log

- **WHEN** the merch-discovery CronJob emits a log entry with severity ERROR
- **THEN** the merch-discovery-specific Alert Policy detects the log entry and opens an Incident

#### Scenario: WARN-level log does not trigger alert

- **WHEN** any workload emits a log entry with severity WARNING
- **THEN** no Alert Policy SHALL fire

## ADDED Requirements

### Requirement: Discovery CronJob failure observability

Backend discovery CronJobs (`concert-discovery`, `sales-phase-discovery`, `merch-discovery`) handle their own errors and exit with status 0 even when a run fails, so that a broken run does not retry into the same persistent fault and exhaust downstream API quota. On this *handled*-failure path the process catches the error, logs it at severity ERROR, and exits 0 — so the Kubernetes Job is reported as succeeded and the ERROR log is the only failure signal. ERROR-log alerting is therefore the correct layer for the handled path, and every backend discovery CronJob SHALL have ERROR-log alert coverage under "Error log detection per workload". Introducing a new discovery CronJob without a corresponding Alert Policy is a violation of this requirement.

This requirement covers ONLY the handled-failure path. Abrupt-termination failures (OOM-kill, image-pull failure, node preemption/eviction) do not reach the handler: the container is killed before it can log an ERROR, and the Job is reported as failed rather than succeeded. Such failures are caught by neither ERROR-log alerting nor (deliberately excluded) Job-level alerting, and remain a separate, currently-uncovered observability gap tracked outside this change.

#### Scenario: Handled failure — job logs ERROR and exits 0

- **WHEN** a discovery CronJob encounters a handled fatal error (for example, DI initialization or a database ping timeout)
- **THEN** the process SHALL log the failure at severity ERROR
- **AND** the process SHALL exit 0 (the Job is reported as succeeded and is NOT retried)
- **AND** the workload's ERROR-log Alert Policy SHALL open an Incident from that ERROR log

#### Scenario: Abrupt termination is out of scope

- **WHEN** a discovery CronJob is abruptly terminated (OOM-kill, image-pull failure, node preemption) before it can log an ERROR
- **THEN** the ERROR-log Alert Policy SHALL NOT be expected to fire (no ERROR log exists)
- **AND** this failure class is acknowledged as a separate, currently-uncovered gap, not addressed by this requirement

#### Scenario: New discovery CronJob is introduced

- **WHEN** a new backend discovery CronJob is added
- **THEN** a per-workload ERROR-log Alert Policy SHALL be created for it in the same `pulumi up` that deploys the job
- **AND** the absence of such a policy SHALL be treated as a spec violation
