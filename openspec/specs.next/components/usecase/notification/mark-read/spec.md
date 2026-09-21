# Mark Read

## Purpose

TBD - created by archiving change introduce-notification-service. Update Purpose after archive.

## Requirements

### Requirement: Mark a notification as read or dismissed
The service SHALL let a user mark a notification (by `notification_id`) as read or dismissed, scoped to that user, recording the transition timestamp. Repeating the same transition SHALL be a no-op (idempotent), and a user SHALL NOT be able to change another user's notification state.

#### Scenario: Marking a notification read is idempotent and user-scoped
- **WHEN** a user marks their own notification as read, then marks it read again
- **THEN** the first call SHALL record `read_at` and the second SHALL be a no-op
- **AND** a request to mark a notification belonging to a different user SHALL be rejected
