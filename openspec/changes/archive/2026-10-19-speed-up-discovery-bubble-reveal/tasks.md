## 1. Reveal-timing measurement first (frontend; route/discovery "Cold-load reveal timings are reported"; D5)

- [x] 1.1 Add `Events.DiscoveryReveal` (`perf.discovery_reveal`) with typed props `entry`, `path`, `seed_count`, `ghosts_ms`, `first_name_ms`, `all_names_ms` in `services/analytics-events.ts`. Verify `make check` passes (the `EventPropsMap` `satisfies` clause compiles)
- [x] 1.2 Record the `discovery:ghosts`, `discovery:first-name` and `discovery:all-names` marks in the bubble canvas and report them to the route. In the route, send the event once per cold visit (ghosts painted by `prepareEntry`), with `entry` from first-route detection, and never after `detaching`. Verify unit tests annotated `@spec` pass for the scenarios "Cold visit with followed artists", "Re-entry", "Analytics off" and "Leaving before the reveal completes"
- [x] 1.4 Load the fan's follows before the initial load in `DiscoveryRoute.refreshField`, and fire the `discovery:ghosts` mark on the first bubble drawn when no ghost is drawn. Verify route tests annotated `@spec` pass for "User has followed artists (Step 1-b)" and "Artists arrive before a ghost is drawn", then release it before the 1.3 baseline
- [x] 1.3 Open the frontend PR, merge after green CI and release it. Then record about 10 owner cold loads per path (`top`, `seed_similar`) on a phone, and write the medians of the three timings per path and `entry` under "Measurements" in design.md. Verify the events appear in PostHog with all properties set

## 2. Proto (specification; adapter/fan/api/rpc/artist; D6)

- [x] 2.1 Change `ListSimilarRequest.limit` to `lte: 50` in `proto/liverty_music/rpc/artist/v1/artist_service.proto`, and update its comment. Verify `buf lint` and `buf format` pass and buf-pr-checks is green (add the `buf skip breaking` label if the breaking check flags it)
- [x] 2.2 Merge the PR, cut the GitHub Release, and verify `buf-release.yml` succeeds and BSR publishes the generated packages

## 3. Backend (usecase/artist/list-similar, list-top, search; adapter/fan/api/rpc/artist; D6)

- [x] 3.1 Bump the generated proto package to the release from 2.2. Verify `make check` passes, and that a handler test annotated `@spec` for "Similar-artist limit too large" fails a limit of 51 with InvalidArgument before the usecase runs
- [x] 3.2 In `ArtistUseCase.ListSimilar`, key the cache by artist id only, look up a fixed 50 (`similarLookupLimit`) from the catalog, and return the first `limit` (all of them for 0). Verify usecase unit tests annotated `@spec` pass for "Known and new similar artists", "Result without MBID", "Limit given", "Limit of zero", "No similar artists", "Repeated call" and "Repeated call with a different limit"
- [x] 3.3 Set the usecase `MemoryCache` TTL to 6 h in `internal/di/provider.go`. Verify unit tests annotated `@spec` pass for "Result older than 6 hours" (ListSimilar, ListTop, Search) and the ListTop and Search "Repeated call" / "Repeated query" scenarios, with an injected clock or a short-TTL cache in the test
- [x] 3.4 Open the backend PR, merge after green CI, and after the prod rollout verify in the fan-api access logs that a second cold load within 6 h shows `ListSimilar` at 0 ms for repeated seeds

## 4. Frontend reveal (route/discovery; D1, D2, D9)

- [x] 4.1 Make ghost bubbles ignore pointer taps and the keyboard focus cycle. Verify unit tests annotated `@spec` pass for "Tap on a ghost" and "Tap on a revealed artist while other bubbles are still ghosts"
- [x] 4.2 Add the `keepGhosts` reconcile mode in `BubblePhysics`, and have the canvas reconcile every field (real members take ghost slots in place, leftover ghosts are kept until an all-real field). Verify `bubble-physics.spec.ts` covers a mixed field (ghosts kept, real members spawned in ghost slots) and an all-real field (leftover ghosts fade out)
- [x] 4.3 Reveal per seed in `ArtistBubbleStore.loadInitial` through an `onPartial` commit that does not touch the seen-tracker, and keep the final `setField` path unchanged. Verify `artist-bubble-store.spec.ts` tests annotated `@spec` pass for "Seed results are revealed as each seed answers", "Progressive reveal converges to the all-at-once field", "A failed seed does not hold back the others", "User has followed artists (Step 1-b)", "Seed selection with fewer than 5 followed artists" and "Cold visit uses ghost bubbles"
- [x] 4.4 Start the top-up `listTop` together with the seed calls, and use it only when the similar results are below 30. Verify tests annotated `@spec` pass for "Sparse seed-similar results are topped up", "Empty seed-similar still fills the field", "Sufficient seed-similar results are not diluted" and "Top-up does not wait for a second round trip"
- [x] 4.5 Make `loadSimilar` await an in-flight initial load instead of returning `false`. Verify a unit test shows that a tap during the reveal adds similar artists after the load and raises no "similar unavailable" snack

## 5. Frontend rendering and delivery (route/discovery; D3, D4, D7, D8)

- [x] 5.1 Split the frame delta: capped `physicsDelta` for `Engine.update`, real elapsed time for the spawn and fade progress. Verify unit tests annotated `@spec` with a fake clock pass for "Normal frame rate", "Slow frames" and "Reduced motion" (name drawn within 300 ms at 16 ms and 100 ms frames)
- [x] 5.2 Move the shrink-and-wrap loop into `computeLabelLayout` and cache it per `${name}|${r}`, cleared above 1,000 entries. Verify a parity unit test over Latin, CJK and mixed names (injected measure function) shows identical font and lines to the old per-frame code
- [x] 5.3 Export `preloadPhysics()` and call it from `DiscoveryRoute.loading()`. Verify a route unit test asserts the import is requested in `loading()`
- [x] 5.4 Add `encode zstd gzip` and the `/assets/*` immutable `Cache-Control` to the `Caddyfile`. Verify `caddy validate` passes in the image build, and after release that `curl -sI -H 'Accept-Encoding: zstd, gzip'` on a hashed `/assets/*.js` shows `content-encoding` and `cache-control: public, max-age=31536000, immutable`, while `/config.json` stays `no-store`, `/sw.js` stays `no-cache`, and an `/events/<id>` page still renders its link-preview tags
- [x] 5.5 Open the frontend PR, merge after green CI and release it
- [x] 5.6 Key the label layout on the bubble's full radius and draw it scaled during the spawn (D4 amendment). Verify a canvas unit test shows one layout per bubble across spawn frames, the label drawn scaled while spawning and unscaled at full size, and the D4 parity test still passing
- [x] 5.7 Compile request-validation rules in an idle callback and pass the first request of a type through (D10). Verify `validate-interceptor.spec.ts` shows the first request forwarded unvalidated with compilation scheduled, and the next request after the idle callback rejected with InvalidArgument; then open the frontend PR, merge after green CI and release it
- [x] 5.8 Replay the analytics pre-init queue in idle slices (D11). Verify `analytics-service.spec.ts` shows one event per slice, a capture during the replay queued behind it, and direct captures once drained; then open the frontend PR, merge after green CI and release it. After release, verify with a trace that no CEL compilation or queue replay sits between `FollowService/List` and the `ListSimilar` requests, and that `measureText` runs once per bubble
- [x] 5.9 Reveal ghosts in place: full size, fading up from the ghost opacity (D1 amendment). Verify `bubble-physics.spec.ts` shows the swapped bubble at scale 1 from the ghost opacity with the name drawn within 64 ms at 16 ms frames, and a tap-added bubble still popping from scale 0
- [x] 5.10 Binary-search the label font steps with a per-layout width cache (D4 amendment). Verify the parity test still matches the per-step loop and a test shows fewer than half the measurements for a long name; then open the frontend PR, merge after green CI and release it
- [x] 5.11 Load the signed-in follow list at boot (`FollowPrefetchTask`) and share it with Discovery (`FollowStore.ensureLoaded`) (D12). Verify follow-store, prefetch-task and route tests show one shared load, a retry after failure and no load for guests
- [x] 5.12 Remove the waste found by the load-path audit (D12): seed limit spread over the display capacity (spec "User has followed artists (Step 1-b)", "Seed selection with fewer than 5 followed artists"), screen-reader count from the field, canvas DPR at most 2, validator module loaded when idle, no synchronous banner height read, long-frame events capped per page, Background Sync only for write RPCs. Verify `make check` and the new unit tests; then open the frontend PR, merge after green CI and release it
- [x] 5.13 Set `Access-Control-Max-Age` to 7200 on the API CORS handler (D12). Verify a handler test and, after the rollout, a production preflight showing `access-control-max-age: 7200`

## 6. Before and after (integration)

- [x] 6.1 Repeat the 1.3 procedure after groups 3–5 are live and add the "after" medians to "Measurements" in design.md. The reveal criterion is replaced by the cold-load budget (D13, group 7); record that the first name now comes about 400 ms after the first bubble and that the data arrives before the first bubble

## 7. Cold-load time budget (route/discovery "Cold load meets a time budget"; D13)

- [x] 7.1 Record profiled traces of a signed-in and a guest repeat-visit cold load on the reference setup, attribute the time to the first bubble to its causes, and record the breakdown and the ordered plan in D13
- [x] 7.2 Draw ghost bubbles before the physics engine is loaded and initialized, so the first bubble does not wait for it. Verify canvas unit tests show ghosts drawn on the first frame after attach without physics, and the reveal scenarios still passing
- [x] 7.3 Remove from the path to the first render what Discovery does not need, in the order of 7.1 (for example user hydration blocking the first render, the router waiting for every route chunk, the `config.json` round trip). Verify each with unit tests and a trace
  - [x] 7.3a Measure each label string once at a reference font size (561 ms of `measureText` for a guest's 30 labels at 4x)
  - [x] 7.3b Request `config.json` from `index.html` (`public/config-prefetch.js`) so it overlaps with the entry script
  - [x] 7.3c Let an app opened on Discovery render before user hydration; routes behind auth wait for it in the auth hook
  - [x] 7.3d Start the initial load during start-up for an app opened on Discovery (spec "Initial load starts during start-up when the app opens on Discovery"); a cold visit is the field's first display in the page
  - [x] 7.3e Serve `config.json` stale-while-revalidate from the service worker and delete the kept copy when a new service worker activates. Verify unit tests for the first start, the kept copy with a background refresh, a failed refresh, an error response, and offline with nothing kept
  - [x] 7.3f Remove the generic pre-hydration skeleton from `index.html`. The sign-in callback, which renders nothing until its canLoad finishes (1 to 4.5 s in prod), shows a static spinner instead. Verify the "Merge progress indication" E2E
- [x] 7.4 Release, then measure about 10 loads each for a signed-in fan with follows and a guest on the reference setup, and record the medians of `ghosts_ms`, `first_name_ms` and first name − ghosts under "Measurements". Verify the first-name bounds of "Cold load meets a time budget" (≤ 6.0 s signed in, ≤ 3.0 s guest). v1.107.0: 5,008 ms signed in, 1,745 / 2,545 ms guest. The signed-in gap between the follow list and `ListSimilar` is frontend#801

