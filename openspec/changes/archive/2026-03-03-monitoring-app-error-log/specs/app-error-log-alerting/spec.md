## ADDED Requirements

### Requirement: Notification via Google Chat and Email

The system SHALL send alert notifications to both a Google Chat Space and an Email address when an Incident is opened.

Notification Channels SHALL be provisioned as Pulumi resources using configuration values (Chat Space ID, Email address) stored in Pulumi ESC.

#### Scenario: ERROR log triggers notifications

- **WHEN** an Alert Policy detects an ERROR log and opens an Incident
- **THEN** a notification SHALL be sent to the configured Google Chat Space
- **AND** a notification SHALL be sent to the configured Email address
