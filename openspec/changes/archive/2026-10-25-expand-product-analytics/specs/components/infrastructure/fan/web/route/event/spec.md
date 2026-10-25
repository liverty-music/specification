## ADDED Requirements

### Requirement: Sharing and adding to a calendar are reported

When the fan uses the share control or the add-to-calendar control of the Event page, the page SHALL send one usage analytics event naming the control, with the Event; for share, it SHALL also state whether the share completed or was cancelled where the device reports it.

#### Scenario: Share
- **WHEN** a fan shares the Event page and completes the share
- **THEN** one share event is sent with the Event and the share completed
