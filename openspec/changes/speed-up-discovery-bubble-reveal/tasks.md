## 1. Reveal-timing measurement first (frontend; route/discovery "Cold-load reveal timings are reported"; D5)

- [ ] 1.1 Add `Events.DiscoveryReveal` (`perf.discovery_reveal`) with typed props `entry`, `path`, `seed_count`, `ghosts_ms`, `first_name_ms`, `all_names_ms` in `services/analytics-events.ts`. Verify `make check` passes (the `EventPropsMap` `satisfies` clause compiles)
- [ ] 1.2 Record the `discovery:ghosts`, `discovery:first-name` and `discovery:all-names` marks in the bubble canvas and report them to the route. In the route, send the event once per cold visit (ghosts painted by `prepareEntry`), with `entry` from first-route detection, and never after `detaching`. Verify unit tests annotated `@spec` pass for the scenarios "Cold visit with followed artists", "Re-entry", "Analytics off" and "Leaving before the reveal completes"
- [ ] 1.3 Open the frontend PR, merge after green CI and release it. Then record about 10 owner cold loads per path (`top`, `seed_similar`) on a phone, and write the medians of the three timings per path and `entry` under "Measurements" in design.md. Verify the events appear in PostHog with all properties set

## 2. Proto (specification; adapter/fan/api/rpc/artist; D6)

- [ ] 2.1 Change `ListSimilarRequest.limit` to `lte: 50` in `proto/liverty_music/rpc/artist/v1/artist_service.proto`, and update its comment. Verify `buf lint` and `buf format` pass and buf-pr-checks is green (add the `buf skip breaking` label if the breaking check flags it)
- [ ] 2.2 Merge the PR, cut the GitHub Release, and verify `buf-release.yml` succeeds and BSR publishes the generated packages

## 3. Backend (usecase/artist/list-similar, list-top, search; adapter/fan/api/rpc/artist; D6)

- [ ] 3.1 Bump the generated proto package to the release from 2.2. Verify `make check` passes, and that a handler test annotated `@spec` for "Similar-artist limit too large" fails a limit of 51 with InvalidArgument before the usecase runs
- [ ] 3.2 In `ArtistUseCase.ListSimilar`, key the cache by artist id only, look up a fixed 50 (`similarLookupLimit`) from the catalog, and return the first `limit` (all of them for 0). Verify usecase unit tests annotated `@spec` pass for "Known and new similar artists", "Result without MBID", "Limit given", "Limit of zero", "No similar artists", "Repeated call" and "Repeated call with a different limit"
- [ ] 3.3 Set the usecase `MemoryCache` TTL to 6 h in `internal/di/provider.go`. Verify unit tests annotated `@spec` pass for "Result older than 6 hours" (ListSimilar, ListTop, Search) and the ListTop and Search "Repeated call" / "Repeated query" scenarios, with an injected clock or a short-TTL cache in the test
- [ ] 3.4 Open the backend PR, merge after green CI, and after the prod rollout verify in the fan-api access logs that a second cold load within 6 h shows `ListSimilar` at 0 ms for repeated seeds

## 4. Frontend reveal (route/discovery; D1, D2, D9)

- [ ] 4.1 Make ghost bubbles ignore pointer taps and the keyboard focus cycle. Verify unit tests annotated `@spec` pass for "Tap on a ghost" and "Tap on a revealed artist while other bubbles are still ghosts"
- [ ] 4.2 Add the `keepGhosts` reconcile mode in `BubblePhysics`, and have the canvas reconcile every field (real members take ghost slots in place, leftover ghosts are kept until an all-real field). Verify `bubble-physics.spec.ts` covers a mixed field (ghosts kept, real members spawned in ghost slots) and an all-real field (leftover ghosts fade out)
- [ ] 4.3 Reveal per seed in `ArtistBubbleStore.loadInitial` through an `onPartial` commit that does not touch the seen-tracker, and keep the final `setField` path unchanged. Verify `artist-bubble-store.spec.ts` tests annotated `@spec` pass for "Seed results are revealed as each seed answers", "Progressive reveal converges to the all-at-once field", "A failed seed does not hold back the others", "User has followed artists (Step 1-b)", "Seed selection with fewer than 5 followed artists" and "Cold visit uses ghost bubbles"
- [ ] 4.4 Start the top-up `listTop` together with the seed calls, and use it only when the similar results are below 30. Verify tests annotated `@spec` pass for "Sparse seed-similar results are topped up", "Empty seed-similar still fills the field", "Sufficient seed-similar results are not diluted" and "Top-up does not wait for a second round trip"
- [ ] 4.5 Make `loadSimilar` await an in-flight initial load instead of returning `false`. Verify a unit test shows that a tap during the reveal adds similar artists after the load and raises no "similar unavailable" snack

## 5. Frontend rendering and delivery (route/discovery; D3, D4, D7, D8)

- [ ] 5.1 Split the frame delta: capped `physicsDelta` for `Engine.update`, real elapsed time for the spawn and fade progress. Verify unit tests annotated `@spec` with a fake clock pass for "Normal frame rate", "Slow frames" and "Reduced motion" (name drawn within 300 ms at 16 ms and 100 ms frames)
- [ ] 5.2 Move the shrink-and-wrap loop into `computeLabelLayout` and cache it per `${name}|${r}`, cleared above 1,000 entries. Verify a parity unit test over Latin, CJK and mixed names (injected measure function) shows identical font and lines to the old per-frame code
- [ ] 5.3 Export `preloadPhysics()` and call it from `DiscoveryRoute.loading()`. Verify a route unit test asserts the import is requested in `loading()`
- [ ] 5.4 Add `encode zstd gzip` and the `/assets/*` immutable `Cache-Control` to the `Caddyfile`. Verify `caddy validate` passes in the image build, and after release that `curl -sI -H 'Accept-Encoding: zstd, gzip'` on a hashed `/assets/*.js` shows `content-encoding` and `cache-control: public, max-age=31536000, immutable`, while `/config.json` stays `no-store`, `/sw.js` stays `no-cache`, and an `/events/<id>` page still renders its link-preview tags
- [ ] 5.5 Open the frontend PR, merge after green CI and release it

## 6. Before and after (integration)

- [ ] 6.1 Repeat the 1.3 procedure on the same phone after groups 3–5 are live, and add the "after" medians to "Measurements" in design.md. Verify `first_name_ms − ghosts_ms` on the `seed_similar` path is at or below the time of the first `ListSimilar` response plus 300 ms. If frames still stall after the reveal, record that the sprite follow-up (design Non-Goals) is needed
