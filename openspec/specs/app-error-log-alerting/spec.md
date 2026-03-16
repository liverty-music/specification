# App Error Log Alerting

## Requirements

### Requirement: Error log detection per workload

The system SHALL detect ERROR-level log entries from each backend workload (server, consumer, concert-discovery) independently using Cloud Monitoring Log-Based Alert Policies.

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

#### Scenario: WARN-level log does not trigger alert

- **WHEN** any workload emits a log entry with severity WARNING
- **THEN** no Alert Policy SHALL fire

### Requirement: Atlas Operator migration failure detection

The system SHALL detect Atlas Operator migration failures using a Cloud Monitoring Log-Based Alert Policy.

The Alert Policy SHALL filter logs by:
- `resource.type = "k8s_container"`
- `resource.labels.namespace_name = "atlas-operator"`
- `resource.labels.container_name = "manager"`
- `jsonPayload.reason` matching `TransientErr` or `BackoffLimitExceeded`

#### Scenario: Atlas migration fails with a transient error

- **WHEN** Atlas Operator logs a `TransientErr` event for a migration failure
- **THEN** the Alert Policy SHALL detect the log entry and open an Incident
- **AND** a Slack notification SHALL be sent to the configured channel

#### Scenario: Atlas migration exceeds backoff limit

- **WHEN** Atlas Operator logs a `BackoffLimitExceeded` event
- **THEN** the Alert Policy SHALL detect the log entry and open an Incident
- **AND** a Slack notification SHALL be sent to the configured channel

#### Scenario: Atlas migration succeeds

- **WHEN** Atlas Operator successfully applies migrations
- **THEN** no Alert Policy SHALL fire

### Requirement: Atlas migration alert uses same notification and rate limiting as backend alerts

The Atlas migration Alert Policy SHALL use the same Slack notification channels, 12-hour rate limit, and 1-hour auto-close settings as the existing backend workload alerts.

#### Scenario: Multiple migration failures within 12 hours

- **WHEN** multiple migration failure log entries occur within a 12-hour window
- **THEN** only the first occurrence SHALL trigger a Slack notification

### Requirement: Notification via Slack

The system SHALL send alert notifications to a configured Slack channel when an Incident is opened.

Slack Notification Channels MUST be created manually through the GCP Console because the GCP API requires an OAuth flow with Slack that cannot be performed via IaC tools (Pulumi/Terraform). The channel ID is then stored in Pulumi ESC and referenced by Pulumi alert policies.

#### Scenario: ERROR log triggers Slack notification

- **WHEN** an Alert Policy detects an ERROR log and opens an Incident
- **THEN** a notification SHALL be sent to the configured Slack channel

#### Scenario: Slack Notification Channel is created via GCP Console

- **WHEN** a new environment needs Slack alerts
- **THEN** the Slack Notification Channel SHALL be created via GCP Console (Monitoring > Alerting > Edit notification channels > Slack)
- **AND** the channel ID SHALL be stored in Pulumi ESC under `monitoring.slackNotificationChannels.alertBackend`

### Requirement: Notification via Google Chat

The system SHALL send alert notifications to a configured Google Chat space when an Incident is opened, in addition to the existing Slack notification.

Google Chat Notification Channels SHALL be created as Pulumi resources (type: `google_chat`) using the `space_id` stored in Pulumi ESC. Unlike Slack channels, Google Chat channels do not require manual GCP Console creation.

Each environment (dev, prod) SHALL have its own Google Chat space for alert notifications.

#### Scenario: ERROR log triggers Google Chat notification

- **WHEN** an Alert Policy detects an ERROR log and opens an Incident
- **THEN** a notification SHALL be sent to the configured Google Chat space
- **AND** a notification SHALL also be sent to the configured Slack channel (parallel operation)

#### Scenario: Atlas migration failure triggers Google Chat notification

- **WHEN** the Atlas migration Alert Policy detects a failure and opens an Incident
- **THEN** a notification SHALL be sent to the configured Google Chat space
- **AND** a notification SHALL also be sent to the configured Slack channel (parallel operation)

#### Scenario: Google Chat Notification Channel is created via Pulumi

- **WHEN** `pulumi up` is executed with `monitoring.googleChatSpaces.alertBackend` configured in ESC
- **THEN** a `gcp.monitoring.NotificationChannel` resource SHALL be created with type `google_chat` and label `space_id` from ESC

#### Scenario: Google Chat space requires Monitoring app pre-installed

- **WHEN** a new environment needs Google Chat alerts
- **THEN** the Google Cloud Monitoring app SHALL be installed in the target Chat space before running `pulumi up`
- **AND** the `space_id` SHALL be stored in Pulumi ESC under `monitoring.googleChatSpaces.alertBackend`

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

All monitoring resources (Alert Policies, Notification Channels, API enablement) SHALL be managed as Pulumi resources in `cloud-provisioning/src/gcp/components/monitoring.ts`.

Slack Notification Channels are referenced (not created) by Pulumi. They are created manually via GCP Console and their channel IDs are stored in Pulumi ESC.

Google Chat Notification Channels are created and managed by Pulumi as `gcp.monitoring.NotificationChannel` resources using `space_id` from Pulumi ESC.

#### Scenario: Pulumi deployment creates monitoring resources

- **WHEN** `pulumi up` is executed
- **THEN** the Alert Policies and Error Reporting API enablement SHALL be created or updated as defined in the Pulumi code
- **AND** the Slack Notification Channel SHALL be referenced by its channel ID from Pulumi ESC
- **AND** the Google Chat Notification Channel SHALL be created with its space_id from Pulumi ESC
- **AND** all Alert Policies SHALL include both Slack and Google Chat notification channels
