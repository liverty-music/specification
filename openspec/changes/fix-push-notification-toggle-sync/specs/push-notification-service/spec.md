## ADDED Requirements

### Requirement: PushSubscription entity model

The system SHALL represent a browser Web Push subscription as a `PushSubscription` entity in `liverty_music.entity.v1`, composed of type-safe wrapper messages rather than inline primitive fields.

#### Scenario: PushSubscription aggregate shape

- **WHEN** a `PushSubscription` entity is serialized
- **THEN** it SHALL carry `id` (`PushSubscriptionId`, UUID wrapper), `user_id` (`UserId`), `endpoint` (`PushEndpoint`), and `keys` (`PushKeys`)
- **AND** `PushSubscriptionId.value` SHALL be a UUID string validated by `protovalidate` `string.uuid`
- **AND** `PushEndpoint.value` SHALL be validated as a URI with `max_len = 2048`
- **AND** `PushKeys` SHALL carry `p256dh` (Base64url, `min_len = 1`, `max_len = 256`) and `auth` (Base64url, `min_len = 1`, `max_len = 64`)

#### Scenario: No inline primitive subscription fields in request messages

- **WHEN** any RPC in `PushNotificationService` accepts or returns push subscription materials
- **THEN** the materials SHALL be expressed via `PushEndpoint`, `PushKeys`, or `PushSubscription` entity messages
- **AND** raw `string endpoint`, `string p256dh`, or `string auth` fields SHALL NOT appear directly in request or response messages

### Requirement: Create RPC registers the calling browser's subscription

The system SHALL expose `PushNotificationService.Create` to register a browser push subscription for the authenticated user. The operation SHALL be an UPSERT keyed by `endpoint`.

#### Scenario: Successful registration

- **WHEN** an authenticated client calls `Create` with a valid `PushEndpoint` and `PushKeys`
- **THEN** the backend SHALL persist a `push_subscriptions` row associating the user with that endpoint
- **AND** if a row with the same endpoint already exists, the keys SHALL be updated (UPSERT)
- **AND** the response SHALL return the resulting `PushSubscription` entity

#### Scenario: Unauthenticated request

- **WHEN** `Create` is called without a valid user session
- **THEN** the service SHALL return `UNAUTHENTICATED`

#### Scenario: Invalid request payload

- **WHEN** `Create` is called with a missing or malformed `PushEndpoint` or `PushKeys`
- **THEN** the service SHALL return `INVALID_ARGUMENT`

### Requirement: Get RPC returns the subscription for a specific browser

The system SHALL expose `PushNotificationService.Get` to retrieve the push subscription uniquely identified by the pair `(user_id, endpoint)`.

#### Scenario: Successful retrieval

- **WHEN** an authenticated client calls `Get` with its own `user_id` and a `PushEndpoint` that matches an existing row for that user
- **THEN** the service SHALL return the matching `PushSubscription` entity

#### Scenario: Subscription not found

- **WHEN** `Get` is called with a `user_id` / `endpoint` pair that does not match any row
- **THEN** the service SHALL return `NOT_FOUND`
- **AND** the response SHALL NOT carry an empty `PushSubscription` placeholder

#### Scenario: Caller attempts to query another user's subscription

- **WHEN** `Get` is called with a `user_id` that differs from the userID extracted from the authenticated session
- **THEN** the service SHALL return `PERMISSION_DENIED`
- **AND** the service SHALL NOT leak whether a subscription exists for that user/endpoint

#### Scenario: Unauthenticated request

- **WHEN** `Get` is called without a valid user session
- **THEN** the service SHALL return `UNAUTHENTICATED`

### Requirement: Delete RPC removes only the specified browser's subscription

The system SHALL expose `PushNotificationService.Delete` to remove the push subscription uniquely identified by `(user_id, endpoint)`. The operation SHALL be idempotent.

#### Scenario: Successful deletion

- **WHEN** an authenticated client calls `Delete` with its own `user_id` and the `PushEndpoint` of one of its registered browsers
- **THEN** the backend SHALL remove exactly that row
- **AND** other rows belonging to the same user (other browsers) SHALL be left untouched

#### Scenario: Idempotent deletion

- **WHEN** `Delete` is called with a `(user_id, endpoint)` pair that does not match any row
- **THEN** the service SHALL return a successful empty response

#### Scenario: Caller attempts to delete another user's subscription

- **WHEN** `Delete` is called with a `user_id` that differs from the userID extracted from the authenticated session
- **THEN** the service SHALL return `PERMISSION_DENIED`
- **AND** no rows SHALL be deleted

#### Scenario: Unauthenticated request

- **WHEN** `Delete` is called without a valid user session
- **THEN** the service SHALL return `UNAUTHENTICATED`

### Requirement: Per-browser scoping for repository operations

The system's `PushSubscriptionRepository` interface SHALL expose exclusively per-browser operations keyed by `(user_id, endpoint)` for mutation and retrieval, plus a batch list for internal push delivery.

#### Scenario: Repository surface

- **WHEN** any component inside the backend needs to mutate or read push subscription state
- **THEN** it SHALL use one of: `Create(sub)`, `Get(userID, endpoint)`, `Delete(userID, endpoint)`, or `ListByUserIDs(userIDs)`
- **AND** `ListByUserIDs` SHALL be used only by the push delivery path, not by any externally triggered RPC

#### Scenario: No bulk-per-user mutation

- **WHEN** any component needs to remove push subscriptions
- **THEN** the removal SHALL be scoped to a single `(user_id, endpoint)` pair
- **AND** no helper SHALL exist that deletes all subscriptions for a user in a single call

### Requirement: Stale subscription self-healing on the client

The system SHALL recover from the "browser has subscription but backend does not" divergence automatically, without requiring user interaction, provided the user has already granted browser notification permission.

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
- **THEN** the UI toggle SHALL reflect the OFF state
- **AND** the system SHALL NOT call `Create` or `Get`

#### Scenario: Self-heal failure degrades to OFF

- **WHEN** the self-heal `Create` call fails
- **THEN** the UI toggle SHALL reflect the OFF state
- **AND** the system SHALL surface the error via standard frontend error handling
