## Why

Users report that the onboarding follow flow has "no response" after tapping artist bubbles. Investigation revealed that follow itself works correctly, but the downstream concert search pipeline is completely broken due to two issues:

1. **Backend**: The `ConcertSearcher` Gemini API call fails with 401 CREDENTIALS_MISSING because a bare `http.Client` is passed, bypassing ADC (Application Default Credentials).
2. **Frontend**: `dev.liverty-music.app` uses a production build where the log level is hardcoded to `warn`, suppressing all INFO-level logs from FollowService and ConcertService, making the issue invisible to developers.

## What Changes

- **Backend**: Stop passing a custom `http.Client` to `NewConcertSearcher`. Use `nil` to let the genai SDK manage ADC authentication. Apply timeout via `context.WithTimeout` at the call site instead.
- **Frontend**: Make the log level configurable via the `VITE_LOG_LEVEL` environment variable instead of relying on Vite's build-mode flag (`import.meta.env.DEV`). Default to `debug` for dev, `info` for prod.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `auto-concert-discovery`: Use SDK-managed ADC authentication for Gemini API calls in concert search
- `frontend-observability`: Make log level configurable per deployment environment

## Impact

- **backend**: `internal/di/provider.go` — change `httpClient` argument from `&http.Client{Timeout: 60s}` to `nil`
- **backend**: `internal/usecase/concert_uc.go` — apply `context.WithTimeout` at the Gemini search call site
- **frontend**: `src/main.ts` — resolve log level from `VITE_LOG_LEVEL` environment variable
- **frontend**: `.env` / `Dockerfile` — add `VITE_LOG_LEVEL` configuration
