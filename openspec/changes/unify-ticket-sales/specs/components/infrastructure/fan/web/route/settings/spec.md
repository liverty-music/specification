# Spec Delta

## ADDED Requirements

### Requirement: The fan edits their name and phone number

The settings screen SHALL show the fan's saved full name and phone number, say that they are shown on the face of the fan's tickets, and let the fan change them with UserService.Update. A phone number SHALL be entered in the domestic form and sent in E.164 form.

#### Scenario: Fan changes their phone number
- **WHEN** a fan with the saved phone number 090-1234-5678 enters 090-9876-5432 and saves
- **THEN** UserService.Update is called with `+819098765432` and the screen shows the new number

#### Scenario: No details saved yet
- **WHEN** a fan who never gave a name or phone number opens the settings screen
- **THEN** both fields are empty and can be filled in

## MODIFIED Requirements

### Requirement: Stale subscription self-healing on settings load

The system SHALL keep the browser's push subscription and the backend's stored subscription convergent automatically, without requiring user interaction, whenever the user has already granted browser notification permission. Recovery SHALL cover both divergence directions:

- **Backend missing the browser's subscription** — the browser has an active subscription the backend does not know about.
- **Browser missing a subscription entirely** — the browser has no active subscription (e.g., after the push service invalidated it, a `410 Gone` cleanup on the backend, a PWA reinstall, or site-data clearing), even though permission is still granted.

In the second case, when permission is granted, the system SHALL create a fresh browser subscription with the configured VAPID application server key and register it via `PushSubscriptionService.Create`. The system SHALL NOT leave a permission-granted user silently unsubscribed. When permission is NOT granted, the system SHALL surface an OFF/re-enable affordance rather than silently doing nothing.

#### Scenario: Self-heal on settings page load

- **WHEN** the settings page loads
- **AND** `PushManager.getSubscription()` returns a non-null subscription
- **AND** `PushSubscriptionService.Get` returns `NOT_FOUND` for that endpoint
- **THEN** the system SHALL call `PushSubscriptionService.Create` with the browser's existing subscription material
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
- **AND** SHALL register the resulting subscription via `PushSubscriptionService.Create`
- **AND** on success the UI toggle SHALL reflect the ON state
- **AND** the user SHALL NOT be prompted to re-grant notification permission

#### Scenario: Self-heal failure degrades to OFF

- **WHEN** the self-heal `subscribe()` or `Create` call fails
- **THEN** the UI toggle SHALL reflect the OFF state
- **AND** the system SHALL surface the error via standard frontend error handling
- **AND** SHALL NOT swallow the failure silently

### Requirement: Subscription registration failures are observable on the client

Push subscription registration (`PushManager.subscribe()` and the `PushSubscriptionService.Create` RPC) SHALL NOT fail silently. Failures SHALL be logged on the client and reflected in the notification toggle state, so a user who believes they enabled notifications is not left silently unsubscribed.

#### Scenario: subscribe() throws during enable

- **WHEN** the user enables notifications
- **AND** `PushManager.subscribe()` throws
- **THEN** the failure SHALL be logged on the client
- **AND** the UI toggle SHALL reflect the OFF (not-enabled) state
- **AND** the user SHALL NOT be shown a success state

### Requirement: Push Notification Toggle
The system SHALL allow users to control push notification delivery for the current browser session. The toggle's displayed state SHALL be derived from the backend push subscription record combined with the browser's `PushManager` state — never from `localStorage`.

#### Scenario: Toggle state on page load — subscribed on this browser
- **WHEN** the Settings page loads
- **AND** `PushManager.getSubscription()` returns a non-null subscription
- **AND** `PushSubscriptionService.Get(endpoint)` returns an existing `PushSubscription`
- **THEN** the Push Notifications toggle SHALL display ON

#### Scenario: Toggle state on page load — not subscribed on this browser
- **WHEN** the Settings page loads
- **AND** `PushManager.getSubscription()` returns `null`
- **THEN** the Push Notifications toggle SHALL display OFF
- **AND** the system SHALL NOT call `PushSubscriptionService.Get` for a non-existent endpoint

#### Scenario: Toggle state on page load — browser has subscription but backend does not (self-heal)
- **WHEN** the Settings page loads
- **AND** `PushManager.getSubscription()` returns a non-null subscription
- **AND** `PushSubscriptionService.Get` returns `NOT_FOUND`
- **THEN** the system SHALL call `PushSubscriptionService.Create` with the browser's existing subscription material
- **AND** on success, the Push Notifications toggle SHALL display ON
- **AND** the user SHALL NOT be shown a permission prompt during self-heal

#### Scenario: Toggling notifications ON
- **WHEN** a user toggles the Push Notifications switch ON
- **THEN** the system SHALL call `PushManager.subscribe()` and `PushSubscriptionService.Create` with the resulting subscription material
- **AND** on success, the toggle SHALL reflect ON
- **AND** the system SHALL NOT write any `localStorage` flag for this state

#### Scenario: Toggling notifications OFF (this browser only)
- **WHEN** a user toggles the Push Notifications switch OFF
- **THEN** the system SHALL call `PushSubscriptionService.Delete(endpoint)` with the current browser's endpoint
- **AND** the system SHALL call `PushSubscription.unsubscribe()` on the browser subscription object
- **AND** other browsers registered by the same user SHALL continue to receive notifications
- **AND** the toggle SHALL reflect OFF

#### Scenario: Toggle state is not cached in localStorage
- **WHEN** the Settings page is rendered
- **THEN** the system SHALL NOT read `localStorage['userNotificationsEnabled']` to determine toggle state
- **AND** the `userNotificationsEnabled` key SHALL NOT appear in the `StorageKeys` catalog
