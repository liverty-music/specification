## Tasks

All tasks target the `backend` repository.

### 1. Add `ListByMBIDs` to `ArtistRepository`

- [x] Add `ListByMBIDs(ctx context.Context, mbids []string) ([]*Artist, error)` to `ArtistRepository` interface in `entity/artist.go`
- [x] Implement in `infrastructure/database/rdb/artist_repo.go` using `unnest + WITH ORDINALITY` pattern
- [x] Add unit test in `artist_repo_test.go`
- [x] Regenerate mocks (`mockery`)

### 2. Extract `persistArtists` helper in UseCase

- [x] Add private method `persistArtists(ctx, []*entity.Artist) ([]*entity.Artist, error)` to `artistUseCase` in `usecase/artist_uc.go`
- [x] Implement: ListByMBIDs → determine missing → Create missing → merge preserving input order
- [x] Add unit tests for the helper (all existing, all new, mixed, empty input)

### 3. Refactor `Search` with dedup + persist

- [x] After `artistSearcher.Search()`, filter out entries with empty MBID
- [x] Dedup by MBID keeping first occurrence
- [x] Replace direct return with `persistArtists()` call
- [x] Update unit tests to verify dedup behavior and DB persistence

### 4. Refactor `ListSimilar` to use helper

- [x] Filter out empty MBID entries from `artistSearcher.ListSimilar()` results
- [x] Replace `artistRepo.Create(ctx, artists...)` with `persistArtists()` call
- [x] Update unit tests

### 5. Refactor `ListTop` to use helper

- [x] Filter out empty MBID entries from `artistSearcher.ListTop()` results
- [x] Replace `artistRepo.Create(ctx, artists...)` with `persistArtists()` call
- [x] Update unit tests

### 6. Verify

- [x] `make check` passes (lint + test)
