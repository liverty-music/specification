## ADDED Requirements

### Requirement: Persist Push Subscriptions

The system SHALL store browser Web Push subscription data (endpoint, p256dh key, auth secret) associated with a user. One user MAY have multiple subscriptions (multiple devices/browsers).

#### Scenario: Registering a new push subscription

- **WHEN** an authenticated user calls `PushNotificationService.Subscribe` with a valid endpoint, p256dh, and auth
- **THEN** the system SHALL create a record in the `push_subscriptions` table linking the subscription to the user
- **AND** the RPC response SHALL indicate success

#### Scenario: Re-registering an existing endpoint

- **WHEN** a user calls `Subscribe` with an endpoint that already exists in the database
- **THEN** the system SHALL update the existing record with the new p256dh and auth values (UPSERT by endpoint)
- **AND** the user_id SHALL be updated to the authenticated user

#### Scenario: Subscribing without authentication

- **WHEN** an unauthenticated request calls `PushNotificationService.Subscribe`
- **THEN** the system SHALL reject the request with an Unauthenticated error

### Requirement: Remove Push Subscriptions

The system SHALL allow users to remove all their push subscriptions.

#### Scenario: Unsubscribing all devices

- **WHEN** an authenticated user calls `PushNotificationService.Unsubscribe`
- **THEN** the system SHALL delete all `push_subscriptions` records for that user

#### Scenario: Unsubscribing with no existing subscriptions

- **WHEN** a user with no push subscriptions calls `Unsubscribe`
- **THEN** the system SHALL return success without error (idempotent)

### Requirement: Deliver Push Notifications for New Concerts

The system SHALL send Web Push notifications to all followers of an artist when new concerts are discovered for that artist. Notifications SHALL be batched per artist (one notification per artist per job run, regardless of how many concerts were found).

#### Scenario: New concerts found for an artist with followers

- **WHEN** `SearchNewConcerts` returns one or more new concerts for an artist
- **AND** the artist has followers with active push subscriptions
- **THEN** the system SHALL send one Web Push notification per subscription
- **AND** the notification payload SHALL include the artist name, the count of new concerts, and a URL to the artist's concert list

#### Scenario: New concerts found but no followers have subscriptions

- **WHEN** `SearchNewConcerts` returns new concerts for an artist
- **AND** no followers of that artist have push subscriptions
- **THEN** the system SHALL skip notification delivery without error

#### Scenario: Push endpoint returns 410 Gone

- **WHEN** the Web Push protocol returns HTTP 410 for a subscription endpoint
- **THEN** the system SHALL delete that subscription from the database
- **AND** continue processing remaining subscriptions

#### Scenario: Push delivery failure (non-410)

- **WHEN** a push send fails with an error other than 410
- **THEN** the system SHALL log the error with subscription details
- **AND** continue processing remaining subscriptions (non-fatal)

#### Scenario: Notification dispatch failure does not affect job

- **WHEN** the notification dispatch step fails entirely for an artist
- **THEN** the concert discovery job SHALL log the error
- **AND** continue processing the next artist (non-fatal, does not increment circuit breaker)

### Requirement: VAPID Authentication

The system SHALL authenticate push messages using VAPID (Voluntary Application Server Identification) with keys managed via environment variables.

#### Scenario: Sending a push notification

- **WHEN** the system sends a Web Push message
- **THEN** it SHALL sign the request using the VAPID private key loaded from configuration
- **AND** the VAPID subject SHALL be a mailto: URI

### Requirement: Service Worker Push Event Handling

The frontend Service Worker SHALL receive and display push notifications.

#### Scenario: Receiving a push event

- **WHEN** the Service Worker receives a push event with a JSON payload
- **THEN** it SHALL display a notification with the title, body, icon, and badge from the payload
- **AND** the notification SHALL use a tag of `concert-{artistID}` to deduplicate per artist

#### Scenario: Clicking a notification

- **WHEN** a user clicks a displayed push notification
- **THEN** the Service Worker SHALL check for an existing app window via `clients.matchAll()`
- **AND** if an existing window is found, it SHALL focus that window
- **AND** if no existing window is found, it SHALL open a new window at the URL from the notification payload

### Requirement: Notification Permission Management

The frontend SHALL manage browser notification permission state reactively and request permission only after explicit user interaction.

#### Scenario: Monitoring permission state

- **WHEN** the app loads
- **THEN** the `NotificationManager` service SHALL query the current notification permission state via `navigator.permissions.query()`
- **AND** SHALL watch for permission state changes via the `change` event

#### Scenario: Requesting permission (soft ask)

- **WHEN** a user taps the notification opt-in prompt in the dashboard
- **THEN** the system SHALL call `Notification.requestPermission()`
- **AND** if granted, SHALL automatically subscribe via `PushManager.subscribe()` and send the subscription to the backend

#### Scenario: Permission already denied

- **WHEN** the notification permission state is `denied`
- **THEN** the opt-in prompt SHALL display guidance to enable notifications via browser settings
- **AND** SHALL NOT call `Notification.requestPermission()`
