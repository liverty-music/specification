## Tasks

All tasks target the `backend` repository. Requires `deduplicate-artist-search` to be merged first.

### 1. Add `ARTIST` stream and event definitions

- [x] Add `ARTIST` stream config to `infrastructure/messaging/streams.go`
- [x] Add `SubjectArtistCreated = "ARTIST.created"` to `infrastructure/messaging/cloudevents.go`
- [x] Add `ArtistCreatedData` struct to `infrastructure/messaging/events.go`

### 2. Add `UpdateName` to `ArtistRepository`

- [x] Add `UpdateName(ctx context.Context, id string, name string) error` to `ArtistRepository` interface in `entity/artist.go`
- [x] Implement in `infrastructure/database/rdb/artist_repo.go`
- [x] Add unit test in `artist_repo_test.go`
- [x] Regenerate mocks (`mockery`)

### 3. Add publisher to `artistUseCase`

- [x] Add `message.Publisher` field to `artistUseCase` struct
- [x] Update `NewArtistUseCase` constructor signature
- [x] Update DI wiring in `di/provider.go` to pass publisher
- [x] Publish `ARTIST.created` events in `persistArtists` for newly created artists
- [x] Update unit tests (mock publisher)

### 4. Implement `ArtistNameConsumer`

- [x] Create `adapter/event/artist_consumer.go` with `ArtistNameConsumer`
- [x] Implement `Handle`: parse event → MusicBrainz GetArtist → UpdateName if differs
- [x] Add unit tests in `artist_consumer_test.go`

### 5. Wire consumer into Router

- [x] Add `ArtistNameConsumer` instantiation in `di/consumer.go`
- [x] Register `resolve-artist-name` handler on `SubjectArtistCreated`

### 6. Verify

- [x] `make check` passes (lint + test)
