## 1. Core: `pkg/httpx` RetryTransport

- [x] 1.1 Create `pkg/httpx/retry.go` with `RetryTransport` implementing `http.RoundTripper` — exponential backoff via `cenkalti/backoff/v5`, retries on 429/503/504, parses `Retry-After` header (delta-seconds and HTTP-date), replays request body via `GetBody`
- [x] 1.2 Add functional options: `WithMaxRetries`, `WithInitialInterval`, `WithMaxInterval`
- [x] 1.3 Create `pkg/httpx/retry_test.go` — unit tests using `httptest.Server`: retry on 429/503/504, no retry on 400/401/404, Retry-After respect, context cancellation during backoff, POST body replay, all retries exhausted

## 2. Integrate: Google Maps client

- [x] 2.1 Wire `RetryTransport`-enabled `http.Client` into `google.NewClient` via DI (`internal/di/provider.go`)
- [x] 2.2 Verify existing Google Maps tests pass with the new transport

## 3. Integrate: Last.fm client (throttle + retry)

- [x] 3.1 Add retry loop around `throttler.Do` in `lastfm.client.get()` using `backoff.Retry` — retry wraps the throttle call so backoff waits don't block the throttle slot
- [x] 3.2 Add/update tests for Last.fm client verifying retry on 429 after throttle

## 4. Integrate: MusicBrainz client (throttle + retry)

- [x] 4.1 Add retry loop around `throttler.Do` in each MusicBrainz method using `backoff.Retry` — same pattern as Last.fm
- [x] 4.2 Add/update tests for MusicBrainz client verifying retry on 503 after throttle

## 5. Refactor: Gemini retry with `cenkalti/backoff`

- [x] 5.1 Replace hand-rolled `for attempt := range maxAttempts` loop in `gemini.searcher.Search()` with `backoff.Retry()`, using existing `isRetryable()` as the permanent-error predicate
- [x] 5.2 Update `gemini/retry_test.go` to work with the new backoff-based implementation — same test scenarios, same behavioral assertions

## 6. Promote dependency

- [x] 6.1 Run `go mod tidy` to promote `cenkalti/backoff/v5` from indirect to direct in `go.mod`
