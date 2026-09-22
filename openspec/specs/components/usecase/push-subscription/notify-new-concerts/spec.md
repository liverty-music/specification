# Notify New Concerts

## Purpose

Notifies a user's subscribed devices when concerts matching their followed artists are newly discovered, sending a localized message that deep-links to the earliest matching concert.

## Requirements

### Requirement: Localize the concert-discovery follower notification body

The system SHALL localize the concert-discovery follower notification that is sent when new concerts are found for a followed artist. The `title` SHALL be the artist name (language-independent) and the `body` SHALL state the count of newly discovered concerts in the recipient's resolved language.

#### Scenario: Body in English

- **WHEN** newly discovered concerts are notified to a recipient resolved to `en`
- **THEN** the `body` SHALL read "1 new concert found" for a single concert
- **AND** the `body` SHALL read "N new concerts found" for N concerts where N is greater than one

#### Scenario: Body in Japanese

- **WHEN** newly discovered concerts are notified to a recipient resolved to `ja`
- **THEN** the `body` SHALL state the new-concert count in Japanese (e.g. "新しいライブが N 件見つかりました")

#### Scenario: Title and deep-link unaffected by language

- **WHEN** a concert-discovery notification is built for any recipient
- **THEN** the `title` SHALL be the artist name regardless of language
- **AND** the `url` SHALL deep-link to the artist's concerts and the `tag` SHALL deduplicate per artist, both regardless of language

### Requirement: Delivery scope limited to newly created concerts

When notifying followers about newly created concerts for an artist, the system SHALL use only the set of concerts that were just created in the triggering operation — not the artist's full upcoming schedule. Hype-level filtering, notification payload content, and delivery decisions SHALL all be computed against this new-concert set.

Furthermore, for each individual recipient the system SHALL narrow the new-concert set to the recipient's **hype-matched subset** — the new concerts that satisfy that recipient's hype-level predicate (`away`/`anywhere` → all; `home` → new concerts in the recipient's home area; `nearby` → new concerts within range of the recipient's home centroid). The notification body count and the deep-link target concert SHALL both be computed from this per-recipient matched subset, never from the unfiltered new-concert set.

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

#### Scenario: Notification count reflects the recipient's matched subset

- **WHEN** 2 new concerts are created for an artist that already has 10 upcoming concerts
- **AND** a follower with `hype = away` exists
- **THEN** the notification payload SHALL report the count as `2`
- **AND** the count SHALL NOT include the pre-existing upcoming concerts

#### Scenario: Home-hype count excludes out-of-area new concerts

- **WHEN** 3 new concerts are created for an artist — 1 in admin area `JP-13` and 2 in admin area `JP-40`
- **AND** a follower with `hype = home` whose home area is `JP-13` exists
- **THEN** the follower SHALL receive a push notification
- **AND** the notification payload SHALL report the count as `1`
- **AND** the count SHALL NOT include the 2 `JP-40` concerts that did not match the recipient's home area

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

### Requirement: New-concert notification deep-links to the earliest matched concert

The new-concert push notification payload SHALL carry a `data.url` that deep-links to a specific concert: the **earliest concert in the recipient's hype-matched subset**. "Earliest" SHALL be determined by concert local date ascending, tie-broken by start time ascending. The URL SHALL take the form `/concerts/<concertId>`, reusing the frontend's canonical concert-detail URL, and SHALL NOT carry a redundant artist filter query parameter (the artist is derivable from the concert).

#### Scenario: Deep-link targets the earliest matched concert

- **WHEN** a recipient's hype-matched subset for an artist contains concerts on 2026-09-10 and 2026-09-03
- **THEN** the notification payload `data.url` SHALL be `/concerts/<id-of-2026-09-03-concert>`

#### Scenario: Same-day matched concerts tie-broken by start time

- **WHEN** a recipient's hype-matched subset contains two concerts both dated 2026-09-03, starting at 18:00 and 19:30
- **THEN** the notification payload `data.url` SHALL point to the 18:00 concert

#### Scenario: Home recipient deep-links to their in-area concert, not the globally earliest

- **WHEN** new concerts are created for an artist — one in `JP-40` on 2026-09-01 and one in `JP-13` on 2026-09-05
- **AND** a follower with `hype = home` whose home area is `JP-13` exists
- **THEN** that follower's notification `data.url` SHALL point to the `JP-13` 2026-09-05 concert
- **AND** SHALL NOT point to the earlier `JP-40` concert that did not match the recipient's home area
