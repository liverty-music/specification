## ADDED Requirements

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
- **THEN** the request SHALL carry an `ArtistId` and a repeated `ConcertId`
- **AND** the request SHALL be validated via `protovalidate`
- **AND** the `ConcertId` list SHALL be non-empty (`min_items = 1`)

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
