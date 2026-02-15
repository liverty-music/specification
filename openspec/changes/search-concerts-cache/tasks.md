## 1. Database Migration

- [ ] 1.1 Create Atlas migration for `latest_search_logs` table (artist_id PK, FK to artists.id, searched_at timestamptz NOT NULL)

## 2. Entity & Repository Layer

- [ ] 2.1 Add `SearchLog` entity struct with `ArtistID` and `SearchedAt` fields
- [ ] 2.2 Define `SearchLogRepository` interface with `GetByArtistID(ctx, artistID)` and `Upsert(ctx, artistID)` methods
- [ ] 2.3 Implement `SearchLogRepository` in the RDB infrastructure layer using UPSERT (`INSERT ... ON CONFLICT DO UPDATE`)

## 3. UseCase Layer

- [ ] 3.1 Add `SearchLogRepository` dependency to `ConcertUseCase` constructor
- [ ] 3.2 Modify `SearchNewConcerts` to check search log before Gemini call — skip if searched within 24 hours and return empty slice
- [ ] 3.3 Add search log upsert at the end of `SearchNewConcerts` after successful Gemini search

## 4. Dependency Injection

- [ ] 4.1 Wire `SearchLogRepository` into `ConcertUseCase` in the application bootstrap

## 5. Tests

- [ ] 5.1 Add unit tests for `SearchNewConcerts` cache hit scenario (returns empty, no Gemini call)
- [ ] 5.2 Add unit tests for `SearchNewConcerts` cache miss scenario (calls Gemini, upserts log)
- [ ] 5.3 Add repository tests for search log UPSERT behavior
