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

Backend discovery CronJobs (`concert-discovery`, `sales-phase-discovery`, `merch-discovery`) exit with status 0 even when a run fails, so that a broken run does not retry into the same persistent fault and exhaust downstream API quota. Because the Kubernetes Job is therefore always reported as succeeded, an ERROR-level log entry is the ONLY failure signal. Every backend discovery CronJob SHALL therefore have ERROR-log alert coverage under "Error log detection per workload". Introducing a new discovery CronJob without a corresponding Alert Policy is a violation of this requirement.

#### Scenario: Discovery job fails but exits 0

- **WHEN** a discovery CronJob encounters a fatal error (for example, DI initialization or a database ping timeout)
- **THEN** the process SHALL log the failure at severity ERROR
- **AND** the process SHALL exit 0 (the Job is reported as succeeded and is NOT retried)
- **AND** the workload's ERROR-log Alert Policy SHALL open an Incident from that ERROR log

#### Scenario: New discovery CronJob is introduced

- **WHEN** a new backend discovery CronJob is added
- **THEN** a per-workload ERROR-log Alert Policy SHALL be created for it in the same `pulumi up` that deploys the job
- **AND** the absence of such a policy SHALL be treated as a spec violation
