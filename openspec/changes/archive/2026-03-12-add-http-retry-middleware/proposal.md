## Why

External API clients (Last.fm, MusicBrainz, Google Maps, Gemini) handle rate limit errors inconsistently. Last.fm and MusicBrainz rely solely on in-memory throttling, which breaks when multiple K8s pods or concurrent jobs overlap — hitting rate limits with no retry. Gemini and Blockchain have hand-rolled retry loops with duplicated backoff logic. There is no shared retry infrastructure.

## What Changes

- Add a new `pkg/httpx` package providing an `http.RoundTripper` wrapper with configurable exponential backoff retry (using `cenkalti/backoff/v5`, already in go.mod)
- The RoundTripper retries on transient HTTP status codes (429, 503, 504) and respects `Retry-After` headers
- Wire retry-enabled `http.Client` instances into Last.fm, MusicBrainz, and Google Maps clients via DI
- Replace Gemini's hand-rolled retry loop with `cenkalti/backoff/v5` `Retry()` (SDK client, not HTTP-based — cannot use RoundTripper)
- Adopt "throttle outside, retry inside" pattern: throttle gates the request attempt, retry with backoff happens outside the throttle slot so backoff wait doesn't block other callers

## Capabilities

### New Capabilities

_None — this is an infrastructure-level improvement with no user-facing capability change._

### Modified Capabilities

_None — no spec-level behavior changes. Error codes returned to callers remain the same (`ResourceExhausted`, `Unavailable`, etc.)._

## Impact

- **backend/pkg/httpx/**: New package (retry RoundTripper)
- **backend/pkg/throttle/**: No changes needed
- **backend/internal/infrastructure/music/lastfm/**: Receives retry-enabled `http.Client`; retry loop moves outside throttle
- **backend/internal/infrastructure/music/musicbrainz/**: Same as Last.fm
- **backend/internal/infrastructure/maps/google/**: Receives retry-enabled `http.Client` (currently has no retry at all)
- **backend/internal/infrastructure/gcp/gemini/**: Replace inline retry with `backoff.Retry()`
- **backend/internal/di/**: Wire retry-configured `http.Client` for external API clients
- **Dependencies**: `cenkalti/backoff/v5` promoted from indirect to direct (already in go.mod)
