## Tasks

All tasks target the `backend` repository. Requires `deduplicate-artist-search` to be merged first.

### 1. Add `ARTIST` stream and event definitions

- [ ] Add `ARTIST` stream config to `infrastructure/messaging/streams.go`
- [ ] Add `SubjectArtistCreated = "ARTIST.created"` to `infrastructure/messaging/cloudevents.go`
- [ ] Add `ArtistCreatedData` struct to `infrastructure/messaging/events.go`

### 2. Add `UpdateName` to `ArtistRepository`

- [ ] Add `UpdateName(ctx context.Context, id string, name string) error` to `ArtistRepository` interface in `entity/artist.go`
- [ ] Implement in `infrastructure/database/rdb/artist_repo.go`
- [ ] Add unit test in `artist_repo_test.go`
- [ ] Regenerate mocks (`mockery`)

### 3. Add publisher to `artistUseCase`

- [ ] Add `message.Publisher` field to `artistUseCase` struct
- [ ] Update `NewArtistUseCase` constructor signature
- [ ] Update DI wiring in `di/provider.go` to pass publisher
- [ ] Publish `ARTIST.created` events in `persistArtists` for newly created artists
- [ ] Update unit tests (mock publisher)

### 4. Implement `ArtistNameConsumer`

- [ ] Create `adapter/event/artist_consumer.go` with `ArtistNameConsumer`
- [ ] Implement `Handle`: parse event → MusicBrainz GetArtist → UpdateName if differs
- [ ] Add unit tests in `artist_consumer_test.go`

### 5. Wire consumer into Router

- [ ] Add `ArtistNameConsumer` instantiation in `di/consumer.go`
- [ ] Register `resolve-artist-name` handler on `SubjectArtistCreated`

### 6. Verify

- [ ] `make check` passes (lint + test)
