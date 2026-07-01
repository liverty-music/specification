## ADDED Requirements

### Requirement: Delivered notifications are reported to product analytics
When a notification's channel delivery is recorded as `delivered`, the service SHALL emit a `notification.delivered` product-analytics event attributed to the recipient and keyed by the `notification_id`, exactly once per notification. The emission SHALL be non-fatal: a failure to report analytics SHALL NOT affect the delivery outcome or the stored notification record. A notification whose delivery is `failed` SHALL NOT produce a `notification.delivered` event.

#### Scenario: A delivered notification is reported once
- **WHEN** a notification's web-push send is recorded as `delivered`
- **THEN** exactly one `notification.delivered` analytics event SHALL be emitted, carrying the recipient identity and the `notification_id`

#### Scenario: A failed notification is not reported as delivered
- **WHEN** a notification's delivery is recorded as `failed`
- **THEN** no `notification.delivered` analytics event SHALL be emitted
- **AND** the notification record SHALL still exist for delivery audit

#### Scenario: Analytics failure does not affect delivery
- **WHEN** the analytics pipeline is unavailable at the moment a notification is delivered
- **THEN** the delivery and its stored outcome SHALL be unaffected, and the failure SHALL be logged rather than propagated

### Requirement: Notification opens and dismissals are reported to product analytics
The client SHALL record a `notification.opened` event when the user activates (opens) a delivered notification, and a `notification.dismissed` event when the user dismisses it, each keyed by the `notification_id` carried in the notification. These events SHALL be routed through product analytics such that the user's analytics opt-out is honored (an opted-out user produces no event) and the event is attributed to the interaction time rather than the time it is reported.

#### Scenario: Opening a notification is reported
- **WHEN** the user activates a delivered notification that carries a `notification_id`
- **THEN** a `notification.opened` analytics event keyed by that `notification_id` SHALL be recorded

#### Scenario: Dismissing a notification is reported
- **WHEN** the user dismisses a delivered notification that carries a `notification_id`
- **THEN** a `notification.dismissed` analytics event keyed by that `notification_id` SHALL be recorded

#### Scenario: Opted-out users are not tracked
- **WHEN** a user who has opted out of analytics opens or dismisses a notification
- **THEN** no `notification.opened` or `notification.dismissed` event SHALL be captured
