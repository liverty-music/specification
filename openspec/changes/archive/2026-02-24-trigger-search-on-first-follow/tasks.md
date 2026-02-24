## 1. UseCase Changes

- [x] 1.1 Add `ConcertUseCase` dependency to `artistUseCase` struct and constructor
- [x] 1.2 Add `SearchLogRepository` dependency to `artistUseCase` struct and constructor
- [x] 1.3 Implement `triggerFirstFollowSearch` method: check search log, launch goroutine if not found
- [x] 1.4 Call `triggerFirstFollowSearch` from `Follow()` after successful DB persist (before return)

## 2. DI Wiring

- [x] 2.1 Update Wire provider set to inject `ConcertUseCase` and `SearchLogRepository` into `artistUseCase`

## 3. Tests

- [x] 3.1 Add test: first follow (no search log) triggers `SearchNewConcerts` in background
- [x] 3.2 Add test: subsequent follow (search log exists) does not trigger search
- [x] 3.3 Add test: already-following (ErrAlreadyExists) skips search log check entirely
- [x] 3.4 Add test: search log lookup error logs and skips search
- [x] 3.5 Run existing tests to verify no regressions
