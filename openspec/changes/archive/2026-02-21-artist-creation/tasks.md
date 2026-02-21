## 1. Database Migration

- [x] 1.1 Add UNIQUE index on `artists.mbid` column (`CREATE UNIQUE INDEX CONCURRENTLY idx_artists_mbid_unique ON artists (mbid) WHERE mbid IS NOT NULL AND mbid != ''`)

## 2. Artist Repository — Extend Create to Variadic

- [x] 2.1 Change `ArtistRepository.Create` signature from `Create(ctx, artist *Artist) error` to `Create(ctx, artists ...*Artist) ([]*Artist, error)` in `entity/artist.go`
- [x] 2.2 Implement variadic `Create` in `rdb/artist_repo.go` using `unnest` pattern: INSERT with `ON CONFLICT (mbid) DO NOTHING`, followed by SELECT to return all artists (new + existing) by MBID list
- [x] 2.3 Update all existing callers of `Create` to match new signature
- [x] 2.4 Write unit tests for `Create` — empty args, single artist, multiple artists, duplicate MBIDs, mixed new/existing

## 3. Concert Repository — Unnest Refactor

- [x] 3.1 Refactor `ConcertRepository.Create` in `rdb/concert_repo.go` to use `unnest` arrays for events INSERT
- [x] 3.2 Refactor `ConcertRepository.Create` to use `unnest` arrays for concerts INSERT
- [x] 3.3 Remove `maxConcertsPerBatch` constant and batch loop
- [x] 3.4 Verify existing concert tests pass with refactored implementation

## 4. Artist UseCase — Auto-persist in ListTop/ListSimilar

- [x] 4.1 Update `ListTop` use case to call `artistRepo.Create(artists...)` on external API results before returning
- [x] 4.2 Update `ListSimilar` use case to call `artistRepo.Create(artists...)` on external API results before returning
- [x] 4.3 Write unit tests verifying `ListTop` returns artists with valid IDs
- [x] 4.4 Write unit tests verifying `ListSimilar` returns artists with valid IDs

## 5. Artist Handler — Fix Create MBID Bug

- [x] 5.1 Update `Create` handler in `artist_handler.go` to read `req.Msg.Mbid` and set `artist.MBID = req.Msg.Mbid.Value`
- [x] 5.2 Write unit test verifying MBID is passed through to use case

## 6. Frontend — Wire Follow RPC

- [x] 6.1 Update `followArtist()` in `artist-discovery-service.ts` to call `this.artistClient.follow({ artistId: new ArtistId({ value: artist.id }) })` with error logging
- [x] 6.2 Verify `listFollowedFromBackend()` works end-to-end with persisted follow data
