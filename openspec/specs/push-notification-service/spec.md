# Push Notification Service

## Purpose

Defines the backend `PushNotificationService` capability that registers, retrieves, and removes a browser's Web Push subscription on a per-`(user_id, endpoint)` basis. The service models subscriptions as type-safe `PushSubscription` entities, enforces strict per-browser scoping (no bulk-per-user mutation in the externally triggered surface), and supports a client-side self-healing flow that recovers from the "browser has subscription but backend does not" divergence without prompting the user.

## Requirements

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

### Requirement: Delivery scope limited to newly created concerts

When notifying followers about newly created concerts for an artist, the system SHALL use only the set of concerts that were just created in the triggering operation — not the artist's full upcoming schedule. Hype-level filtering, notification payload content, and delivery decisions SHALL all be computed against this new-concert set.

#### Scenario: Home filter evaluated against new concerts only

- **WHEN** a new concert is created for an artist in admin area `JP-40`
- **AND** the artist also has pre-existing upcoming concerts in admin area `JP-13`
- **AND** a follower with `hype = home` whose home area is `JP-13` exists
- **THEN** the follower SHALL NOT receive a push notification
- **AND** filtering SHALL be computed from the set `{JP-40}`, never `{JP-40, JP-13}`

#### Scenario: Nearby filter evaluated against new concerts only

- **WHEN** a new concert is created for an artist at a venue 300 km from a follower's home centroid
- **AND** the artist also has pre-existing upcoming concerts within 200 km of that follower's home centroid
- **AND** the follower's hype level is `nearby`
- **THEN** the follower SHALL NOT receive a push notification
- **AND** proximity SHALL be computed from only the new concerts

#### Scenario: Notification count reflects new concerts only

- **WHEN** 2 new concerts are created for an artist that already has 10 upcoming concerts
- **AND** a follower with `hype = away` exists
- **THEN** the notification payload SHALL report the count as `2`
- **AND** the count SHALL NOT include the pre-existing upcoming concerts

#### Scenario: No delivery when zero concerts are newly created

- **WHEN** the concert creation operation completes with zero newly created concerts for an artist
- **THEN** the system SHALL NOT trigger the notification pipeline for that artist
- **AND** SHALL NOT publish a `CONCERT.created` event

### Requirement: CONCERT.created event carries identifiers of newly created concerts

The `CONCERT.created` CloudEvent payload SHALL carry the artist identifier and the identifiers of the concerts created in that operation, and SHALL NOT carry any aggregate counter or name fields that can be derived at consumption time.

#### Scenario: Event payload shape

- **WHEN** a `CONCERT.created` event is published
- **THEN** its data payload SHALL contain exactly two fields: `artist_id` (string) and `concert_ids` (array of string)
- **AND** `concert_ids` SHALL contain at least one element
- **AND** each element SHALL be an identifier of a concert created in the triggering operation

#### Scenario: Artist context is resolved at consumption time

- **WHEN** the notification consumer processes a `CONCERT.created` event
- **THEN** it SHALL resolve the artist entity (for the notification body) from the artist identifier at consumption time
- **AND** the event payload SHALL NOT carry `artist_name` or other denormalized artist fields

#### Scenario: No legacy fields retained

- **WHEN** a `CONCERT.created` event is published by this system version
- **THEN** its data payload SHALL NOT contain a `concert_count` field
- **AND** SHALL NOT contain any other field beyond `artist_id` and `concert_ids`

### Requirement: Notification consumer is a thin adapter over the use case

The consumer handler subscribed to `CONCERT.created` SHALL only parse the CloudEvent envelope and delegate to the notification use case. It SHALL NOT perform repository queries, hydrate domain entities, or apply business filters.

#### Scenario: Handler responsibilities

- **WHEN** the `CONCERT.created` consumer receives a message
- **THEN** it SHALL deserialize the CloudEvent data into the use case's input struct
- **AND** invoke the `NotifyNewConcerts` use case method with that struct and the request context
- **AND** propagate the use case's error (if any) unchanged

#### Scenario: Handler has no direct repository dependencies

- **WHEN** the notification consumer is constructed
- **THEN** it SHALL NOT accept `ArtistRepository`, `ConcertRepository`, or any other repository as a dependency
- **AND** all domain-data access required for notification delivery SHALL occur inside the use case

### Requirement: NotifyNewConcerts debug RPC for deterministic invocation

The `PushNotificationService` SHALL expose a `NotifyNewConcerts` RPC that invokes the same delivery path as the `CONCERT.created` consumer, bypassing the event bus. This RPC is intended for integration testing and operator-initiated re-delivery.

#### Scenario: Request shape

- **WHEN** a client calls `PushNotificationService.NotifyNewConcerts`
- **THEN** the request SHALL carry an `ArtistId` and a repeated `EventId` (concerts are identified by the event UUID since `Concert.id` is typed as `EventId`)
- **AND** the request SHALL be validated via `protovalidate`
- **AND** the `EventId` list SHALL be non-empty (`min_items = 1`)

#### Scenario: Successful invocation in non-production

- **WHEN** the RPC is invoked with a valid artist and concert identifiers while the server is configured for a non-production environment (`local`, `development`, or `staging`)
- **THEN** the service SHALL execute the same delivery logic as the `CONCERT.created` consumer
- **AND** SHALL return a successful empty response after the delivery path completes
- **AND** all filtering and payload computation SHALL be scoped to the provided `concert_ids`

#### Scenario: Disabled in production

- **WHEN** the RPC is invoked while the server is configured for the `production` environment
- **THEN** the service SHALL return `PERMISSION_DENIED`
- **AND** no delivery SHALL occur
- **AND** the restriction SHALL be enforced at the server side, independent of client-provided credentials

#### Scenario: Unknown concert identifiers are rejected

- **WHEN** the RPC is invoked with a `concert_id` that does not match any concert for the provided `artist_id`
- **THEN** the service SHALL return `INVALID_ARGUMENT`
- **AND** no partial delivery SHALL occur

#### Scenario: Unauthenticated invocation

- **WHEN** the RPC is invoked without a valid session
- **THEN** the service SHALL return `UNAUTHENTICATED`
- **AND** the response SHALL NOT reveal which environment the server is running in
