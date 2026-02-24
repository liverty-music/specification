## Why

When a user follows an artist for the first time, the system should immediately discover upcoming concerts via Gemini API. Currently, concert search only runs during the onboarding loading sequence or via a periodic CronJob. If the onboarding flow is skipped or the user follows artists outside onboarding, no search is triggered until the next CronJob run.

## What Changes

- The `artistUseCase.Follow()` method will check whether the artist has been searched before (via `searchLogRepo`).
- If no search log exists for the artist, a background goroutine will call `concertUseCase.SearchNewConcerts()` to immediately discover concerts.
- The `artistUseCase` will gain a new dependency on `ConcertUseCase`.
- The existing 24-hour cache in `SearchNewConcerts` ensures no duplicate Gemini API calls if the CronJob or frontend also triggers a search.

## Capabilities

### New Capabilities
- `follow-triggered-search`: Automatically trigger Gemini-based concert discovery when an artist receives their first follow.

### Modified Capabilities

## Impact

- `internal/usecase/artist_uc.go`: Add `ConcertUseCase` dependency; add search trigger logic in `Follow()`.
- `internal/di/`: Wire `ConcertUseCase` into `artistUseCase` constructor.
- `internal/usecase/artist_uc_test.go`: Add test cases for the new background search trigger.
