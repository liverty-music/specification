## 1. Database Migration

- [x] 1.1 Create Atlas migration for `latest_search_logs` table (artist_id PK, FK to artists.id, searched_at timestamptz NOT NULL)

## 2. Entity & Repository Layer

- [x] 2.1 Add `SearchLog` entity struct with `ArtistID` and `SearchedAt` fields
- [x] 2.2 Define `SearchLogRepository` interface with `GetByArtistID(ctx, artistID)` and `Upsert(ctx, artistID)` methods
- [x] 2.3 Implement `SearchLogRepository` in the RDB infrastructure layer using UPSERT (`INSERT ... ON CONFLICT DO UPDATE`)

## 3. UseCase Layer

- [x] 3.1 Add `SearchLogRepository` dependency to `ConcertUseCase` constructor
- [x] 3.2 Modify `SearchNewConcerts` to check search log before Gemini call — skip if searched within 24 hours and return empty slice
- [x] 3.3 Add search log upsert at the end of `SearchNewConcerts` after successful Gemini search

## 4. Dependency Injection

- [x] 4.1 Wire `SearchLogRepository` into `ConcertUseCase` in the application bootstrap

## 5. Tests

- [x] 5.1 Add unit tests for `SearchNewConcerts` cache hit scenario (returns empty, no Gemini call)
- [x] 5.2 Add unit tests for `SearchNewConcerts` cache miss scenario (calls Gemini, upserts log)
- [x] 5.3 Add repository tests for search log UPSERT behavior
