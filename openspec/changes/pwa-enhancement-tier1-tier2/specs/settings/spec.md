## MODIFIED Requirements

### Requirement: Push Notification Toggle
The system SHALL allow users to control push notification delivery.

#### Scenario: Toggling notifications
- **WHEN** a user toggles the Push Notifications switch
- **THEN** the system SHALL subscribe or unsubscribe the user's push subscriptions via the backend `PushNotificationService` RPC
- **AND** when OFF, the system SHALL call `Unsubscribe` to remove all of the user's push subscriptions so no notifications are delivered to any device
- **AND** when ON, the system SHALL call `Subscribe` to register the current device's push subscription for notifications based on followed artists and their passion levels

#### Scenario: VAPID key not configured
- **WHEN** the VAPID public key is not available (environment variable not set)
- **THEN** the push notification toggle SHALL be displayed in a disabled state
- **AND** the system SHALL show a helper text indicating that push notifications are not available in this environment
- **AND** the system SHALL NOT attempt to subscribe or produce a runtime error
