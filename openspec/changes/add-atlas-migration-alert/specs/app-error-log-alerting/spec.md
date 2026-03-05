## ADDED Requirements

### Requirement: Atlas Operator migration failure detection

The system SHALL detect Atlas Operator migration failures using a Cloud Monitoring Log-Based Alert Policy.

The Alert Policy SHALL filter logs by:
- `resource.type = "k8s_container"`
- `resource.labels.namespace_name = "atlas-operator"`
- `resource.labels.container_name = "manager"`
- `textPayload` matching `TransientErr` or `BackoffLimitExceeded`

#### Scenario: Atlas migration fails with non-linear error

- **WHEN** Atlas Operator logs a `TransientErr` event for a migration failure
- **THEN** the Alert Policy SHALL detect the log entry and open an Incident
- **AND** a Slack notification SHALL be sent to the configured channel

#### Scenario: Atlas migration exceeds backoff limit

- **WHEN** Atlas Operator logs a `BackoffLimitExceeded` event
- **THEN** the Alert Policy SHALL detect the log entry and open an Incident

#### Scenario: Atlas migration succeeds

- **WHEN** Atlas Operator successfully applies migrations
- **THEN** no Alert Policy SHALL fire

### Requirement: Atlas migration alert uses same notification and rate limiting as backend alerts

The Atlas migration Alert Policy SHALL use the same Slack notification channels, 12-hour rate limit, and 1-hour auto-close settings as the existing backend workload alerts.

#### Scenario: Multiple migration failures within 12 hours

- **WHEN** multiple migration failure log entries occur within a 12-hour window
- **THEN** only the first occurrence SHALL trigger a Slack notification
