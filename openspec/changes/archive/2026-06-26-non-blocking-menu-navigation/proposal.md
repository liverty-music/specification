## Why

Tapping a bottom-nav menu tab feels slow: the outgoing screen stays frozen until the new page's data finishes loading, because each menu-tab route `await`s its network/RPC fetch inside the Aurelia router `loading()` hook — and the router blocks the view swap until `loading()` resolves. Navigation should feel instant: the new page should attach immediately and show its own spinner/empty state while data streams in.

## What Changes

- Menu-tab routes (My Artists, Dashboard, Discovery) stop `await`ing their data fetch inside `loading()`. The synchronous prelude (toggle `isLoading`, create `AbortController`, hydrate/restore-from-URL, banner state) stays in `loading()`; the fetch is kicked off non-blocking so the view attaches immediately.
- Post-load side effects that today depend on data being awaited before `attached()` (Dashboard's post-signup/guest celebration and onboarding-completion latch) are re-anchored to **data arrival via Aurelia observation (`@watch`)** instead of `attached()` timing — so they still fire only once the timetable is real, matching the existing `needsRegion` non-blocking branch.
- Route unit tests stop asserting populated state synchronously after `loading()`; they await the extracted fetch method (or `tasksSettled()`) deterministically rather than draining timers and hoping.
- No protobuf, RPC, or backend changes. No user-facing copy changes.

## Capabilities

### New Capabilities
- `non-blocking-menu-navigation`: Bottom-nav menu-tab routes attach their view immediately on navigation (render-then-fetch), present their existing loading/empty/error UI while data is in flight, and gate any "data is ready" side effects on observed data arrival rather than on the router awaiting the fetch.

### Modified Capabilities
<!-- None. Celebration/onboarding-latch behavior is unchanged at the requirement level
     (still fires once the timetable is real); only the detection mechanism changes,
     which is an implementation concern captured in design.md. -->

## Impact

- Frontend only (`liverty-music/frontend`):
  - `src/routes/my-artists/my-artists-route.ts` — extract fetch into `loadArtists(signal)`, call non-blocking from `loading()`.
  - `src/routes/dashboard/dashboard-route.ts` — make the region-set branch non-blocking; re-anchor `onTimetableReady()` (celebration + completion latch) to data arrival via `@watch`.
  - `src/routes/discovery/discovery-route.ts` — extract `loadInitialBubbles()`, call non-blocking; rely on the canvas `artistsChanged` (`!this.ctx` guard) + `attached()` seed for order-independence.
  - `test/routes/{my-artists,dashboard,discovery}-route.spec.ts` — deterministic async assertions.
- Builds on the `aurelia-reactivity` capability (`@watch`/`@observable` patterns) and the existing `dashboard-concert-cache` work; coordinates with (but does not require) a future `FollowStore` TTL cache for repeat-visit instantness.
