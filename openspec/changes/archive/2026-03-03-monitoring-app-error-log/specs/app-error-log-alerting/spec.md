## ADDED Requirements

### Requirement: Error log detection per workload

The system SHALL detect ERROR-level log entries from each backend workload (server, consumer, concert-discovery) independently using Cloud Monitoring Log-Based Alert Policies.

Each Alert Policy SHALL filter logs by:
- `resource.type = "k8s_container"`
- `resource.labels.namespace_name = "backend"`
- `resource.labels.container_name` matching the specific workload name
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

#### Scenario: WARN-level log does not trigger alert

- **WHEN** any workload emits a log entry with severity WARNING
- **THEN** no Alert Policy SHALL fire

### Requirement: Notification via Google Chat and Email

The system SHALL send alert notifications to both a Google Chat Space and an Email address when an Incident is opened.

Notification Channels SHALL be provisioned as Pulumi resources using configuration values (Chat Space ID, Email address) stored in Pulumi ESC.

#### Scenario: ERROR log triggers notifications

- **WHEN** an Alert Policy detects an ERROR log and opens an Incident
- **THEN** a notification SHALL be sent to the configured Google Chat Space
- **AND** a notification SHALL be sent to the configured Email address

### Requirement: Notification rate limiting

The system SHALL suppress repeated notifications for the same Incident, sending at most one notification per 12-hour period (`notificationRateLimit.period = 43200s`).

#### Scenario: Multiple ERROR logs within 12 hours

- **WHEN** multiple ERROR log entries match the same Alert Policy within a 12-hour window
- **THEN** only the first occurrence SHALL trigger a notification
- **AND** subsequent occurrences within the same 12-hour window SHALL be suppressed

### Requirement: Incident auto-close

The system SHALL automatically close an Incident after 1 hour (`autoClose = 3600s`) of no matching ERROR log entries.

#### Scenario: ERROR logs stop for 1 hour

- **WHEN** an Incident is open and no matching ERROR log entries occur for 1 hour
- **THEN** the Incident SHALL be automatically closed

#### Scenario: New ERROR after auto-close

- **WHEN** an Incident has been auto-closed and a new ERROR log entry is detected
- **THEN** a new Incident SHALL be opened and a new notification SHALL be sent (subject to the 12-hour rate limit of the previous Incident's last notification)

### Requirement: Error context in alert labels

Each Alert Policy SHALL extract `error_code` and `rpc_method` labels from the matching log entry using `labelExtractors`, so that alert notifications include the error type and the RPC method where the error occurred.

#### Scenario: Notification includes error context

- **WHEN** an ERROR log entry contains `jsonPayload.error.code = "internal"` and `jsonPayload.rpc_method = "/liverty.v1.UserService/GetUser"`
- **THEN** the alert notification SHALL include `error_code: internal` and `rpc_method: /liverty.v1.UserService/GetUser`

### Requirement: Error Reporting API enabled

The system SHALL have the `clouderrorreporting.googleapis.com` API enabled to allow automatic error grouping and first-seen detection for ERROR-level log entries.

#### Scenario: Error Reporting detects errors

- **WHEN** the `clouderrorreporting.googleapis.com` API is enabled
- **AND** ERROR-level log entries are ingested by Cloud Logging
- **THEN** Error Reporting SHALL automatically group and display the errors in the GCP Console

### Requirement: Infrastructure as Code

All monitoring resources (Notification Channels, Alert Policies, API enablement) SHALL be managed as Pulumi resources in `cloud-provisioning/src/gcp/components/monitoring.ts`.

#### Scenario: Pulumi deployment creates monitoring resources

- **WHEN** `pulumi up` is executed
- **THEN** the Notification Channels, Alert Policies, and Error Reporting API enablement SHALL be created or updated as defined in the Pulumi code
