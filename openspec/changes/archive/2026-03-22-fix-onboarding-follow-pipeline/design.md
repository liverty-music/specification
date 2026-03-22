## Context

The onboarding flow's concert search pipeline is completely broken. After a user follows an artist, `SearchNewConcerts` triggers a background Gemini API call that fails with 401 CREDENTIALS_MISSING. The root cause is that `provider.go` passes `&http.Client{Timeout: 60*time.Second}` to `NewConcertSearcher`, which prevents the genai SDK from configuring ADC-based authentication. Additionally, debugging was difficult because `dev.liverty-music.app` uses a production build with log level `warn`, hiding all INFO logs.

## Goals / Non-Goals

**Goals:**
- Gemini API calls authenticate correctly via WIF-based ADC
- Maintain 60-second timeout for concert search operations
- Allow log level to be configured per deployment environment (dev=debug, prod=info)

**Non-Goals:**
- Reworking the concert search retry strategy (existing 3-retry approach is adequate)
- Adding user-facing notification UI for `SEARCH_STATUS_FAILED` (separate change)
- Fixing `EmailParser` (already passes `nil`, works correctly)

## Decisions

### 1. Pass `nil` for HTTPClient — let the SDK manage ADC

**Choice**: Pass `nil` to `NewConcertSearcher` so the genai SDK constructs an ADC-authenticated HTTP client internally.

**Alternatives considered**:
- A) Build ADC transport manually with `golang.org/x/oauth2/google` — unnecessary complexity, SDK does the same internally
- B) Pass authenticated client via `option.WithHTTPClient` — genai SDK uses `ClientConfig.HTTPClient`, not the `option` pattern; manual construction is discouraged

**Rationale**: Google Cloud Go SDK best practice is to not pass custom HTTP clients. The SDK manages credential refresh and transport configuration correctly.

### 2. Use `context.WithTimeout` for timeout control

**Choice**: Apply `context.WithTimeout(ctx, 60*time.Second)` at the `ConcertSearcher.Search()` call site in the usecase layer.

**Rationale**: Recommended by Google Cloud Go SDK documentation. Per-call `context.WithTimeout` provides fine-grained control with proper cancellation propagation, unlike `http.Client.Timeout` which applies globally.

### 3. Keep the `httpClient` parameter for testing

**Choice**: Maintain the `NewConcertSearcher(ctx, cfg, httpClient, logger)` signature. Pass `nil` in production, `httptest.Server` clients in tests.

**Rationale**: Existing unit tests (`searcher_test.go`, `retry_test.go`) rely on `httptest.Server`. No reason to break this pattern.

### 4. Control log level via `VITE_LOG_LEVEL` environment variable

**Choice**: Read `import.meta.env.VITE_LOG_LEVEL` at startup with fallback to `import.meta.env.DEV`.

```
VITE_LOG_LEVEL=debug  → LogLevel.debug  (dev environment)
VITE_LOG_LEVEL=info   → LogLevel.info   (prod environment)
unset + DEV=true      → LogLevel.debug  (local development)
unset + DEV=false     → LogLevel.warn   (fallback)
```

**Rationale**: `import.meta.env.DEV` is a build-time flag, making it impossible to run the same production build with different log levels across environments. `VITE_LOG_LEVEL` is embedded at build time via Vite's env system, but `.env` and Dockerfile `ARG` allow per-environment control.

## Risks / Trade-offs

- **[Test compatibility]** Keeping `httpClient` parameter means zero impact on existing tests → low risk
- **[genai SDK updates]** Default client construction may change in major SDK versions → monitor on upgrade
- **[Build-time log level]** `VITE_LOG_LEVEL` is embedded at build time, requiring a rebuild to change → acceptable; runtime control can be added separately if needed
