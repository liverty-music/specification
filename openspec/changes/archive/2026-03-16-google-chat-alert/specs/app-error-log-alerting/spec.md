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
