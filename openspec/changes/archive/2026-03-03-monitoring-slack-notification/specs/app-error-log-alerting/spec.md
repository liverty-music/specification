## MODIFIED Requirements

### Requirement: Notification via Google Chat and Email

The system SHALL send alert notifications to a configured Slack channel when an Incident is opened.

A single Slack Notification Channel SHALL be provisioned as a Pulumi resource using configuration values (`slackChannelName`, `slackAuthToken`) stored in Pulumi ESC. The `authToken` SHALL be stored in `sensitiveLabels` to prevent exposure via GCP API responses.

#### Scenario: ERROR log triggers Slack notification

- **WHEN** an Alert Policy detects an ERROR log and opens an Incident
- **THEN** a notification SHALL be sent to the configured Slack channel

#### Scenario: Slack auth token is stored securely

- **WHEN** the Slack Notification Channel is provisioned
- **THEN** the `authToken` SHALL be stored in `sensitiveLabels` (not `labels`)
- **AND** the token SHALL be wrapped with `pulumi.secret()` in the Pulumi state

## REMOVED Requirements

### Requirement: Notification via Google Chat and Email
**Reason**: Google Workspace environment does not support Chat or Email. Replaced by Slack notification.
**Migration**: Replace `chatSpaceId` / `notificationEmail` with `slackChannelName` / `slackAuthToken` in Pulumi ESC configuration.
