## Why

`components/usecase/artist/search`'s "Search reports failures" requirement currently states that `ArtistUseCase.Search` "SHALL fail with Internal when Artist.Search fails, whatever its error" — and the shipped code (`liverty-music/backend#504`) does exactly that, collapsing every catalog failure (rate limiting, an outage, a timeout) into a generic Internal error. That throws away information the caller could otherwise act on: a rate-limited search (ResourceExhausted) is retryable, an outage (Unavailable) is not the fan's fault, and both look identical to a genuine bug once flattened to Internal. Every other external-port call in the same use case (`ListSimilar`, `ListTop`, and other usecases' payment/catalog ports) already returns the port's error unchanged, so this is also an inconsistency within the codebase, not just a missed opportunity.

## What Changes

- Change `components/usecase/artist/search`'s "Search reports failures" requirement: `ArtistUseCase.Search` SHALL return `Artist.Search`'s error unchanged (preserving its code — NotFound, Unavailable, ResourceExhausted, DeadlineExceeded, or whatever the catalog port reports), the same as it already does for `Artist.ListByMBIDs` and `Artist.Create`.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `components/usecase/artist/search`: the "Search reports failures" requirement changes from "fails with Internal, whatever Artist.Search's error" to "returns Artist.Search's error unchanged", with scenarios covering Unavailable, ResourceExhausted and DeadlineExceeded catalog failures.

## Impact

- Affected specs: `openspec/specs/components/usecase/artist/search/spec.md`.
- Affected code (backend repo, tracked by `liverty-music/backend#504`): `internal/usecase/artist_uc.go` (`Search` stops wrapping `artistSearcher.Search`'s error with `codes.Internal` and returns it unchanged).
- `components/adapter/fan/api/rpc/artist` was reviewed for consistency: it already treats Search's error as an opaque pass-through (no code-specific handling at the RPC boundary), so no change is needed there.
- No proto or API surface changes.
