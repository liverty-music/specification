## Why

When artists are persisted to the database via Last.fm search results, their display names come from Last.fm which may not match the canonical MusicBrainz name (e.g. Last.fm might store a popular but unofficial variant). There is currently no mechanism to resolve canonical names asynchronously after artist creation.

Additionally, the `persistArtists` helper introduced in `deduplicate-artist-search` knows exactly which artists are newly created. Publishing an `artist.created` event enables downstream consumers to enrich artist data without blocking the search response.

## What Changes

- Add `ARTIST` JetStream stream with `ARTIST.*` subject pattern
- Add `ARTIST.created` subject and `ArtistCreatedData` event payload
- Extend the `persistArtists` helper in `artistUseCase` to publish `ARTIST.created` events for newly inserted artists
- Add `message.Publisher` dependency to `artistUseCase`
- Add `UpdateName` method to `ArtistRepository` for canonical name correction
- Introduce `ArtistNameConsumer` that subscribes to `ARTIST.created`, resolves the canonical name from MusicBrainz, and updates the DB if it differs
- Wire the new consumer into the Watermill Router

## Prerequisites

- `deduplicate-artist-search` must be merged first (provides the `persistArtists` helper and read-then-write pattern that identifies new artists)

## Capabilities

### New Capabilities
- `artist-name-resolution`: Async consumer that resolves canonical artist names from MusicBrainz upon artist creation, keeping the `artists` table aligned with MusicBrainz identity data

### Modified Capabilities
- `event-messaging`: New `ARTIST` JetStream stream added alongside existing `CONCERT` and `VENUE` streams
- `artist-discovery`: `persistArtists` helper now publishes events for newly created artists

## Impact

- **Backend**: Modified files: `usecase/artist_uc.go` (add publisher, publish events in helper), `entity/artist.go` (add `UpdateName` to interface), `infrastructure/database/rdb/artist_repo.go` (implement `UpdateName`), `infrastructure/messaging/streams.go` (add ARTIST stream), `infrastructure/messaging/cloudevents.go` (add subject constant), `infrastructure/messaging/events.go` (add payload type), `di/provider.go` (pass publisher to artist UC), `di/consumer.go` (wire new consumer). New files: `adapter/event/artist_consumer.go`. Mock regeneration required.
- **Frontend**: No changes.
- **Proto (RPC)**: No changes.
- **Database**: No schema migration. `UpdateName` uses a simple `UPDATE artists SET name = $2 WHERE id = $1`.
- **NATS**: New `ARTIST` stream auto-provisioned by `EnsureStreams`.

## Out of Scope

- Artist alias/variant tracking (storing multiple known names per MBID)
- Batch backfill of canonical names for existing artists
- `artist.followed` event (separate concern)
