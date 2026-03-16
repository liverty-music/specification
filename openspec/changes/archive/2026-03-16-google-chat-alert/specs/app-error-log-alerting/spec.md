## ADDED Requirements

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

## MODIFIED Requirements

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
