## Why

On a cold visit to Discovery, the ghost bubbles stay on screen for seconds before artist names appear. For a fan who already follows artists, the initial load waits for every seed's `ListSimilar` call. Production access logs show these calls finishing one after another, about 0.2 s apart, because all catalog lookups share one rate-limited queue. The slowest one takes up to 2.4 s (for example 511 / 1251 / 1935 / 2160 / 2371 ms on 2026-10-16). When the names do start to render, each frame re-measures every label, and the spawn animation is advanced by a delta capped at 32 ms. Slow frames therefore also stretch the time until the names fade in.

## What Changes

- **Progressive reveal.** The cold-visit field shows each seed's similar artists as soon as that seed's lookup returns, in place of ghost bubbles, instead of waiting for every seed. The final field is unchanged: the same invariants, the same top-up rule.
- **Ghost bubbles ignore taps.** Today a tap on a ghost placeholder reaches the follow flow with a placeholder id. A progressive reveal keeps ghosts and real artists on screen together for longer, so ghosts must not react.
- **Top-up fetched concurrently.** The global top artists used to top up a sparse field are requested together with the seed lookups. They are appended only when the similar results fall below 30, as before.
- **Names fade in on real time.** A revealed bubble's name becomes readable within 300 ms of real time at any frame rate. Physics keeps its 32 ms step cap.
- **Label layout computed once.** A bubble's label wrapping and font size are computed once per name and radius, not on every frame. The pixels do not change.
- **Similar-artist cache independent of the limit.** `ArtistUseCase.ListSimilar` always asks the catalog for 50 artists, caches the result per artist, and returns the first `limit` of them. The usecase result cache (similar, top, search) keeps entries for 6 hours instead of 1 hour.
- **BREAKING (request validation):** the fan `ListSimilar` limit range narrows from 0–100 to 0–50. The fan web, the only caller, requests at most 50.
- **Cold-load timings are measured.** One analytics event per cold visit records the time to ghost bubbles, the first name and all names. The before and after can then be compared on real devices in production.
- **Static assets compressed and cached.** The fan web server compresses text assets and serves hashed `/assets/*` files as immutable for one year. Today the 446 KB entry script and other scripts are sent uncompressed, with no cache header.
- **Physics engine fetched earlier.** The physics library chunk is requested when the Discovery route starts loading, not after the canvas is attached.

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `components/infrastructure/fan/web/route/discovery`: the similar-seed initial load reveals per seed. The sparse top-up may be fetched before it is needed. A cold visit switches ghosts to real artists progressively. Three additions: names fade in within a real-time bound, ghost bubbles ignore taps, and cold-load reveal timings are sent as an analytics event.
- `components/usecase/artist/list-similar`: always looks up 50 similar artists and returns the first `limit`. The limit range becomes 0–50. A recent result is reused per artist id for 6 hours, whatever the limit.
- `components/usecase/artist/list-top`: a recent result is reused for 6 hours (was 1 hour).
- `components/usecase/artist/search`: a recent result is reused for 6 hours (was 1 hour).
- `components/adapter/fan/api/rpc/artist`: the `ListSimilar` limit outside 0 to 50 fails with InvalidArgument.

Unchanged:
- The entity operations `Artist.ListSimilar`, `Artist.ListTop` and `Artist.Search` keep their contracts. The usecase only passes a fixed limit of 50 to `Artist.ListSimilar`.
- The `discover-artists` story keeps its registration and announcement rule.
- The admin artist boundary does not expose a `ListSimilar` limit.

## Impact

- **Proto (this repository):** `liverty_music/rpc/artist/v1/artist_service.proto`. The `ListSimilarRequest.limit` changes to `lte: 50`, published to BSR.
- **Backend:**
  - `internal/usecase/artist_uc.go`: the ListSimilar cache key and fixed lookup limit.
  - `internal/di/provider.go`: the cache TTL becomes 6 h.
- **Frontend:**
  - Bubble field owner: `services/artist-bubble-store.ts`.
  - Bubble canvas and physics: `components/dna-orb/dna-orb-canvas.ts`, `components/dna-orb/bubble-physics.ts`.
  - Discovery route: `routes/discovery/discovery-route.ts`.
  - Analytics events: `services/analytics-events.ts`.
  - Web server config: `Caddyfile`.
- **Verification:** the dev environment is stopped. Verification uses unit tests (including one that checks the cached label layout equals the current per-frame layout, since the bubble canvas has no visual-regression baseline) and the new cold-load analytics event in production, released first to record a baseline.
