## MODIFIED Requirements

### Requirement: Stale subscription self-healing on the client

The system SHALL keep the browser's push subscription and the backend's stored subscription convergent automatically, without requiring user interaction, whenever the user has already granted browser notification permission. Recovery SHALL cover both divergence directions:

- **Backend missing the browser's subscription** — the browser has an active subscription the backend does not know about.
- **Browser missing a subscription entirely** — the browser has no active subscription (e.g., after the push service invalidated it, a `410 Gone` cleanup on the backend, a PWA reinstall, or site-data clearing), even though permission is still granted.

In the second case, when permission is granted, the system SHALL create a fresh browser subscription with the configured VAPID application server key and register it via `PushNotificationService.Create`. The system SHALL NOT leave a permission-granted user silently unsubscribed. When permission is NOT granted, the system SHALL surface an OFF/re-enable affordance rather than silently doing nothing.

#### Scenario: Self-heal on settings page load

- **WHEN** the settings page loads
- **AND** `PushManager.getSubscription()` returns a non-null subscription
- **AND** `PushNotificationService.Get` returns `NOT_FOUND` for that endpoint
- **THEN** the system SHALL call `PushNotificationService.Create` with the browser's existing subscription material
- **AND** on success, the UI toggle SHALL reflect the ON state
- **AND** the user SHALL NOT be prompted to re-grant notification permission

#### Scenario: No self-heal when browser has no subscription

- **WHEN** the settings page loads
- **AND** `PushManager.getSubscription()` returns `null`
- **AND** browser notification permission is NOT `granted`
- **THEN** the UI toggle SHALL reflect the OFF state
- **AND** the system SHALL NOT call `Create` or `Get`
- **AND** the system SHALL offer the user an affordance to enable notifications

#### Scenario: Auto re-subscribe when browser has no subscription but permission is granted

- **WHEN** the app resolves push state (e.g., on settings page load or app startup)
- **AND** browser notification permission is `granted`
- **AND** `PushManager.getSubscription()` returns `null`
- **THEN** the system SHALL call `PushManager.subscribe()` with the configured VAPID application server key
- **AND** SHALL register the resulting subscription via `PushNotificationService.Create`
- **AND** on success the UI toggle SHALL reflect the ON state
- **AND** the user SHALL NOT be prompted to re-grant notification permission

#### Scenario: Self-heal failure degrades to OFF

- **WHEN** the self-heal `subscribe()` or `Create` call fails
- **THEN** the UI toggle SHALL reflect the OFF state
- **AND** the system SHALL surface the error via standard frontend error handling
- **AND** SHALL NOT swallow the failure silently

## ADDED Requirements

### Requirement: Service Worker renews the subscription on pushsubscriptionchange

The Service Worker SHALL handle the `pushsubscriptionchange` event. When the push service rotates or expires the subscription, the Service Worker SHALL obtain a new subscription using the configured VAPID application server key and re-register it with the backend via `PushNotificationService.Create`, so that browser-initiated subscription churn does not silently end delivery. Renewal SHALL run without any user interaction and SHALL NOT require the app UI to be open.

#### Scenario: Browser rotates the subscription

- **WHEN** the browser fires `pushsubscriptionchange` in the Service Worker
- **AND** a new subscription can be obtained with the configured VAPID application server key
- **THEN** the Service Worker SHALL subscribe to the push service for the new subscription
- **AND** SHALL register the new subscription with the backend via `PushNotificationService.Create`
- **AND** the user SHALL continue to receive push notifications without re-enabling them

#### Scenario: Renewal cannot obtain a new subscription

- **WHEN** the Service Worker handles `pushsubscriptionchange`
- **AND** a new subscription cannot be obtained (e.g., permission was revoked)
- **THEN** the Service Worker SHALL NOT crash the event
- **AND** the stale endpoint SHALL NOT remain registered as if active

### Requirement: Subscription registration failures are observable on the client

Push subscription registration (`PushManager.subscribe()` and the `PushNotificationService.Create` RPC) SHALL NOT fail silently. Failures SHALL be logged on the client and reflected in the notification toggle state, so a user who believes they enabled notifications is not left silently unsubscribed.

#### Scenario: subscribe() throws during enable

- **WHEN** the user enables notifications
- **AND** `PushManager.subscribe()` throws
- **THEN** the failure SHALL be logged on the client
- **AND** the UI toggle SHALL reflect the OFF (not-enabled) state
- **AND** the user SHALL NOT be shown a success state
