## ADDED Requirements

### Requirement: Notifications are persisted as identified entities
Every user-facing notification SHALL be persisted as a durable record with a stable identifier (`notification_id`), the recipient `user_id`, a `type`, the rendered `payload`, and a `created_at` timestamp, before or at the moment it is dispatched. The record is the source of truth; a dispatch failure SHALL NOT cause the notification to be lost.

#### Scenario: A notification is recorded when produced
- **WHEN** a producer asks the notification service to notify a user (e.g. new concerts, a sales reminder)
- **THEN** a notification record SHALL be created with a unique `notification_id`, the `user_id`, the `type`, the `payload`, and `created_at`
- **AND** the record SHALL exist regardless of whether the channel send subsequently succeeds or fails

### Requirement: Per-notification delivery outcome is recorded
The service SHALL record the delivery outcome of each notification's channel send: `queued` on creation, then `delivered` once the channel accepts the send, or `failed` (with a failure reason) on error, so that "did this notification reach the user?" is answerable from stored state. (Web push provides no separate sent-vs-delivered receipt, so `delivered` denotes acceptance by the push service; a distinct `sent` state is not modelled for this channel.)

#### Scenario: Successful web-push send is recorded as delivered
- **WHEN** the web-push channel send for a notification succeeds
- **THEN** the notification's delivery status SHALL be recorded as `delivered` with a delivery timestamp

#### Scenario: Failed send is recorded as failed, not dropped
- **WHEN** the web-push channel send fails (e.g. the push service rejects it)
- **THEN** the notification's delivery status SHALL be recorded as `failed` with a failure reason
- **AND** the notification record SHALL remain so the failure is auditable and the send is re-dispatchable

### Requirement: All user-facing notifications flow through the notification service
Producers of user-facing notifications SHALL dispatch through the notification service rather than calling the push sender directly, so that every notification a user receives has a corresponding record and delivery outcome. Migrating producers SHALL preserve their existing behaviour (audience resolution, once-only delivery) and the content users receive.

#### Scenario: New-concert and sales-reminder notifications are recorded
- **WHEN** the new-concert notifier or the sales-reminder delivery sends a notification
- **THEN** it SHALL do so through the notification service
- **AND** a notification record with a delivery outcome SHALL exist for that send
- **AND** the user SHALL receive the same web-push content as before

### Requirement: Read and dismiss state is user-controllable and idempotent
The service SHALL let a user mark a notification (by `notification_id`) as read or dismissed, scoped to that user, recording the transition timestamp. Repeating the same transition SHALL be a no-op (idempotent), and a user SHALL NOT be able to change another user's notification state.

#### Scenario: Marking a notification read is idempotent and user-scoped
- **WHEN** a user marks their own notification as read, then marks it read again
- **THEN** the first call SHALL record `read_at` and the second SHALL be a no-op
- **AND** a request to mark a notification belonging to a different user SHALL be rejected

### Requirement: The notification identifier is propagated end-to-end
The `notification_id` SHALL be carried from the stored record into the dispatched push payload (so the client/service worker can reference it), establishing a stable correlation key for later notification-lifecycle features (in-app inbox, and the deferred `notification.opened` / `notification.dismissed` analytics events).

#### Scenario: The push payload carries the notification id
- **WHEN** a notification is dispatched to the web-push channel
- **THEN** the push payload SHALL include the `notification_id` (e.g. in its `data`)
- **AND** that id SHALL match the stored notification record's identifier
