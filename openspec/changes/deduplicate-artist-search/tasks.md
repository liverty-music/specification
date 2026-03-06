## Tasks

All tasks target the `backend` repository.

### 1. Add `ListByMBIDs` to `ArtistRepository`

- [ ] Add `ListByMBIDs(ctx context.Context, mbids []string) ([]*Artist, error)` to `ArtistRepository` interface in `internal/entity/artist.go`
- [ ] Implement in `internal/infrastructure/database/rdb/artist_repo.go` using `unnest + WITH ORDINALITY` pattern
- [ ] Add unit test in `artist_repo_test.go`
- [ ] Regenerate mocks (`mockery`)

### 2. Extract `persistArtists` helper in UseCase

- [ ] Add private method `persistArtists(ctx, []*entity.Artist) ([]*entity.Artist, error)` to `artistUseCase` in `internal/usecase/artist_uc.go`
- [ ] Implement: ListByMBIDs → determine missing → Create missing → merge preserving input order
- [ ] Add unit tests for the helper (all existing, all new, mixed, empty input)

### 3. Refactor `Search` with dedup + persist

- [ ] After `artistSearcher.Search()`, filter out entries with empty MBID
- [ ] Dedup by MBID keeping first occurrence
- [ ] Replace direct return with `persistArtists()` call
- [ ] Update unit tests to verify dedup behavior and DB persistence

### 4. Refactor `ListSimilar` to use helper

- [ ] Filter out empty MBID entries from `artistSearcher.ListSimilar()` results
- [ ] Replace `artistRepo.Create(ctx, artists...)` with `persistArtists()` call
- [ ] Update unit tests

### 5. Refactor `ListTop` to use helper

- [ ] Filter out empty MBID entries from `artistSearcher.ListTop()` results
- [ ] Replace `artistRepo.Create(ctx, artists...)` with `persistArtists()` call
- [ ] Update unit tests

### 6. Verify

- [ ] `make check` passes (lint + test)
