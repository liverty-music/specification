## Context

See proposal.md (Why) for the symptom. These facts were measured or read before this design, on 2026-10-17:

- **Seed lookups queue on the backend.** Production access logs show the similar-seed load's 5 `ListSimilar` calls finishing about 200–250 ms apart (for example 511 / 1251 / 1935 / 2160 / 2371 ms). Every Last.fm call goes through one global throttler: 1 call per 200 ms, FIFO (`backend/internal/infrastructure/music/lastfm/client.go:101,122`). Last.fm allows 5 requests per second, so the throttler stays as it is.
- **Cache hits are cheap, misses are frequent.** `ListTop` on a cache hit takes 0 ms of server time. The usecase cache is one in-process `MemoryCache` with a 1 h TTL (`backend/internal/di/provider.go:239`), shared by the `search:`, `similar:` and `top:` keys. The `similar:` key includes the limit (`artist_uc.go:210`). The fan web asks for `floor(50 / seeds)` per seed and 30 on a tap, so the same artist is often cached under a different limit and missed. Production runs one fan-api pod with 0 restarts, up about 31 h at the time of reading, so the cache is lost mainly on deploys.
- **Fan web callers.** `ListSimilar` is called only by the fan web Discovery route (`artist-bubble-store.ts:263,377`), with at most 50.
- **Label layout runs every frame.** `renderBubbleText` (`dna-orb-canvas.ts:678`) runs per bubble per frame. Each run sets `ctx.font` and calls `wrapText` (per-character `measureText` for CJK names). It repeats this in a loop that shrinks the font by 0.5 px until the label fits. The 2026-03-21 design (`fix-discovery-bubble-content`, design.md:37) assumed `measureText` has "no performance cost". The 2026-03-22 design (`fix-artist-bubble`) added per-character CJK wrapping. The 2026-08-13 design (`refactor-discovery-bubble-field-state`, design.md:174) named this per-frame layout, with the gradient and `shadowBlur` cost, as deferred "measure-first" work. It suggested per-artist offscreen sprites, which change pixels.
- **Spawn speed depends on frame time.** The loop caps the frame delta at 32 ms (`dna-orb-canvas.ts:498`). The cap stops Matter.js from exploding after tab switches and GC pauses, and replaced a 16.7 ms cap that halved physics speed at 30 fps (commit df83606). The same capped delta drives the spawn progress, at 0.003 per ms (`bubble-physics.ts:364`, from #484, about 330 ms). The name is drawn once opacity, the square of progress, exceeds 0.55 (`dna-orb-canvas.ts:657`), at about 247 ms of capped time. At 100 ms frames that becomes about 800 ms of real time.
- **Ghost taps reach the follow flow.** Ghost bubbles are hit-testable. `getBubbleAt` does not skip them, so a tap on a ghost dispatches `artist-selected` with a `__ghost__N` artist into the follow flow.
- **Static assets are uncompressed.** Production `main-*.js` (446 KB) and `preload-helper-*.js` (449 KB) are served without `Content-Encoding` and without `Cache-Control`. The `Caddyfile` has no `encode` directive. The service worker precaches all hashed assets (`sw.ts:28`), so repeat visits already avoid the network. The first visit and every service-worker install download everything uncompressed.
- **Physics engine loads late.** Matter.js is a dynamic import in `BubblePhysics.init()` (`bubble-physics.ts:53`), first called after the canvas is attached and sized. Ghost bubbles cannot be drawn before it resolves.
- **No Chrome trace.** The local headless Chrome could not start (missing `libnspr4`), so this design has no trace. The per-frame label cost is inferred from the code and from the user's DevTools trace, which shows the main thread saturated from the reveal onward. Decision 5 ships the measurement first.

## Goals / Non-Goals

**Goals:**
- Shorten the time from ghost bubbles to readable names on a cold visit, most of all for fans with follows.
- Measure that time on real devices in production, before and after.
- Keep the final field, and the label pixels, exactly as they are now.
- Meet a cold-load time budget on a fixed reference setup (added 2026-10-19, narrowed the same day): first name ≤ 6.0 s signed in, ≤ 3.0 s guest from the page start (medians of about 10 repeat-visit loads, Chrome device emulation at 375 px, Slow 4G and 4x CPU throttling). The first bubble and the first bubble → first name are recorded, not bound (D13).

**Non-Goals:**
- Baking each bubble into an offscreen sprite (gradient, rim blur and label). It is the next step if the measurement still shows heavy frames after Decision 4. It changes pixels, so it is kept out of this change, as the 2026-08-13 design advised.
- Changing the Last.fm throttler, the seed count (5), bubble sizes or physics parameters.
- Re-splitting the JS bundles. This is revisited after compression, from the new numbers.
- Re-entry behavior (cached field, 15-minute reuse), which already paints instantly.

## Decisions

### 1. Reveal seed results as they arrive, inside the field owner

`ArtistBubbleStore.fetchSeedSimilar` takes an `onPartial` callback. Each seed promise, on settle:
1. stores its result at the seed's index;
2. computes `freshFrom(results in seed order so far)`, capped to 50;
3. commits `[...partialReal, ...ghosts.slice(partialReal.length)]` through `commitField`.

The seen-tracker is not touched by partial commits. When every seed has settled, `loadInitial` runs the existing `setField(next)` path unchanged. The final field therefore equals today's all-at-once field (spec: "Progressive reveal converges to the all-at-once field").

The canvas must handle a mixed field. Today `artistsChanged` sees a ghost and only calls `addBubbles` (`dna-orb-canvas.ts:137,155`), which never replaces ghosts. `BubblePhysics.reconcile` gains a `keepGhosts` mode:
- the real members in the target reuse ghost slots in place, through `revealGhostBubbles`, with the spawn animation;
- ghost bodies beyond the real members are kept, not faded out;
- the final all-real field fades out any leftover ghosts, as today.

The canvas calls `reconcile` for every field and passes `keepGhosts` when the field still contains ghosts.

Amended after the after-measurement (2026-10-19): `revealGhostBubbles` restarted the scale-from-zero spawn, so a swapped ghost shrank to nothing, popped back, and showed its name only about 250 ms later. A ghost turning into its artist now stays full size and fades up from the ghost's opacity (0.35) to 1 in about 150 ms (`revealInPlace`), so the name shows about 46 ms after the swap. A bubble added from a tap keeps the pop.

Taps during the reveal: `loadSimilar` returns `false` while `isLoading` is set, which would raise the "similar unavailable" snack for a tap on an early-revealed artist. `loadSimilar` instead awaits the in-flight initial load (kept as a promise) and then runs. The follow itself is optimistic and does not wait. `setField` already excludes followed ids, so an artist followed mid-reveal does not come back in the final field.

Alternatives:
- Reveal on the canvas only, with the field still committed once: rejected. The field is the single source of truth (spec "Physics layer is a pure projection of the field"), and the delay is in the data, not in the drawing.
- One batched RPC for all seeds: rejected. The backend would still queue the 5 Last.fm calls, so the first name would arrive no sooner.
- Fewer seeds: rejected. It changes the field's composition and recommendation quality.

### 2. Request the top-up together with the seeds

When the fan follows artists, `loadInitial` starts `artists.listTop(country, '', 50)` right after dispatching the seed calls. It awaits that promise only if the deduplicated similar results are below 30. The frontend SWR cache and the backend cache (`top:<country>::50`, shared by every fan of the country) make it a cache hit nearly always.

On a backend miss it takes one 200 ms throttler slot, possibly ahead of a seed. This happens at most once per country per cache period, and is accepted. If the field is not sparse, the response is not used.

### 3. Animate spawn and fade on real elapsed time

The loop computes `elapsed = time - lastTime` and keeps `physicsDelta = min(elapsed, 32)`. `BubblePhysics.update(physicsDelta, animDelta)` passes `physicsDelta` to `Engine.update` and `animDelta = elapsed` to the spawn and fade-out progress. The speed stays at 0.003 per ms, so a name is readable after about 247 ms of real time at any frame rate (spec bound: 300 ms).

`animDelta` needs no cap: progress is clamped to 1, and `resume()` resets `lastTime`, so a long pause completes the animation and does nothing worse.

### 4. Compute each label layout once per name and radius

`DnaOrbCanvas` keeps a `Map<string, LabelLayout>` keyed by `${name}|${r}`, with `LabelLayout = { font, lines, lineHeight }`. `computeLabelLayout` is today's shrink-and-wrap loop, moved unchanged. `renderBubbleText` reads the layout, sets `ctx.font` once and draws the lines.

The key uses the exact drawn radius, so the pixels are identical to today. `r` changes only during the spawn frames where the name is visible (progress 0.74 to 1, about 85 ms), so each bubble creates a handful of entries and then always hits. The map is cleared when it exceeds 1,000 entries, which bounds memory over a long session of taps.

The bubble canvas has no visual-regression baseline. Parity is therefore checked by a unit test that runs the old and new layout over a fixture of Latin, CJK and mixed names with an injected measure function.

Alternatives:
- Round the radius in the key: rejected. Fewer misses, but `radius * 0.38` font sizing changes the pixels.
- Sprites: see Non-Goals.

Amended after the production trace (2026-10-19): keying on the drawn radius missed on every spawn frame, because `r = radius × scale` changes each frame, and each miss re-ran the shrink-and-wrap loop (586 ms of `measureText` between the first bubble and the first name at 4x CPU throttling). The layout is now keyed on the bubble's full `radius` and drawn scaled about the center (`ctx.translate` + `ctx.scale`) while `scale ≠ 1`. At full size it is drawn unscaled, so the pixels after the spawn are unchanged; during the spawn (about 85 ms with the name visible) the text scales with the bubble instead of being re-wrapped.

Amended again after the after-measurement: the shrink loop re-wrapped the name at every 0.5 px step. It now binary-searches the same steps and caches each measured width within one layout. Text width grows with the font size, so the search stops at the step the one-by-one loop would; the parity test confirms the same font and lines.

### 5. Report cold-load reveal timings, and ship that first

The canvas records:
- `performance.mark('discovery:ghosts')` when it first draws a bubble: a ghost, or an artist when the artists arrived before the physics engine could draw any ghost (a fast load; without this the event would be lost and the baseline would drop its fastest loads);
- `performance.mark('discovery:first-name')` when it first draws a label;
- `performance.mark('discovery:all-names')` on the first frame where every live bubble is real and past the label threshold.

It reports them to the route through a callback. The route sends one `perf.discovery_reveal` event (new `Events.DiscoveryReveal`, typed props in `analytics-events.ts`, following the existing `perf.*` events). Its properties are `entry`, `path`, `seed_count`, `ghosts_ms`, `first_name_ms` and `all_names_ms`:
- `entry`: `page_load` when Discovery is the document's first route, measured from `performance.timeOrigin`; `in_app` otherwise, measured from `performance.now()` at the route's `loading()`.
- `path`: `top` or `seed_similar`.

The route sends the event only when `prepareEntry` painted ghosts (a cold visit) and only if all three marks fire before `detaching`.

The route loads the fan's follows (`followStore.listFollowed`) before the initial load. Without it, a signed-in fan who opens Discovery directly has an empty follow list at `loadInitial`, takes the top-artists path, and sees followed artists as bubbles, against "User has followed artists (Step 1-b)". Found in the first baseline run (2026-10-17); shipped with the measurement fix before the baseline is recorded again, so the extra round trip is on both sides of the comparison. The analytics service already applies consent and address sanitizing.

The measurement ships in its own frontend release before Decisions 1–4 and 7–8, so production records a baseline. There are only two real users, so the owner records about 10 cold loads per path on their own phone before and after, and the change records the medians below.

### 6. ListSimilar caches one 50-artist lookup per artist; cache TTL 6 h

In `ArtistUseCase.ListSimilar`:
- the key becomes `similar:<artistID>`;
- a cache miss calls `artistSearcher.ListSimilar(ctx, artist, 50)` (constant `similarLookupLimit = 50`), filters by MBID, persists, and caches the full list;
- every call returns `list[:min(limit, len)]`, and the whole list for `limit == 0`.

The proto `ListSimilarRequest.limit` changes to `lte: 50`, matching the only caller. Without that, a request above 50 would silently receive fewer artists than the boundary accepts.

`provider.go` changes the shared `MemoryCache` TTL to 6 h, which also changes `top:` and `search:` (spec deltas for ListTop and Search). Charts and catalog matches do not change materially within hours. A second cache instance just to keep search at 1 h was rejected as an extra moving part with no observed need. The cleanup ticker runs at TTL/6, so 1 h.

Effect and limit: this helps only repeated lookups within 6 hours on the same pod, such as a tap on an artist that was a seed earlier, or a second cold visit. The first lookup of an artist still waits for Last.fm, so Decision 1 carries the cold-visit gain.

### 7. Compress responses and mark hashed assets immutable in Caddy

Inside the `handle` block:
- `encode zstd gzip`;
- `@assets path /assets/*` with `header @assets Cache-Control "public, max-age=31536000, immutable"`.

Vite emits only content-hashed files under `/assets/`. `index.html`, `/config.json` and `/sw.js` keep their current headers.

Caddy orders `encode` before `templates`, so the `/events/*` link-preview HTML is compressed after templating. With the immutable header, a service-worker install can reuse assets the page already downloaded from the HTTP cache instead of downloading them a second time.

Alternative: precompressed `.br`/`.zst` files from the build, served with `file_server precompressed`. Rejected for now: it needs a build plugin and gives a better ratio at no CPU cost, but CPU is irrelevant at current traffic. It is a follow-up if the fan-web pod's CPU ever matters.

### 8. Start the physics engine download on route entry

`bubble-physics.ts` exports `preloadPhysics()`, which calls the same memoized `import('matter-js')`. `DiscoveryRoute.loading()` calls it, so the chunk downloads while the route's template is composed.

A `<link rel="modulepreload">` in `index.html` was rejected: it would fetch the physics engine on every page, not only Discovery.

### 9. Ghost bubbles ignore input

`findClosestBubble` skips bubbles whose artist `isGhost`, which covers pointer taps. The keyboard focus cycle (`onKeyDown`) also skips ghosts.

### 10. Compile request-validation rules when idle

Found in the production trace (2026-10-19): the fan web's protovalidate interceptor (`modernize-protobuf-workflow` D6) compiles a request type's CEL rules on the main thread the first time that type is sent. On a signed-in cold load this ran for 1.86 s at 4x CPU throttling right before the `ListSimilar` requests went out. D6 aimed to keep latency unchanged by loading the validator without blocking; the compilation was not part of that analysis.

The interceptor now passes the first request of a type through unvalidated and compiles that type's rules in a `requestIdleCallback`; later requests of the type are validated. This keeps D6's contract (requests never wait for the validator; the server is authoritative) and extends it to compilation. No code reads the local violations (`cause`), so a first request rejected by the server instead of locally behaves the same for the caller.

Alternatives: validate only write and search RPCs (needs a per-method list that drifts with the schema); precompile every request type at start-up (moves seconds of work into start-up).

### 11. Replay the analytics queue in idle slices

Found in the trace after D10 shipped (2026-10-19): PostHog init (scheduled by `requestIdleCallback` with a 2 s timeout, so it runs inside a slow cold load) replayed every event queued before it in one task, 1.3 s at 4x CPU throttling, between `FollowService/List` finishing and the `ListSimilar` requests. The queue now drains in idle slices, at least one event per slice, and new captures queue behind it so the order is unchanged. Later init was rejected: events of sessions shorter than the delay would be lost.

### 12. Remove waste on the load path

An audit of everything between Discovery's route loading and the first name (2026-10-19, code, traces and the fan-api log) kept the items that are certainly wasted and cheap to change:

- The follow list loads at boot once the session is known (`FollowPrefetchTask`, not blocking start-up) and Discovery reuses that load (`FollowStore.ensureLoaded`), instead of fetching it after the route starts and only then sending the seeds (median 1031 ms between them).
- The seed limit spreads the bubbles the screen shows (30 below 390 px), not always 50.
- The screen-reader status counts the shown real artists from the field instead of observing the physics body map (recomputed on every ghost swap, counting ghosts).
- The canvas renders at a device pixel ratio of at most 2.
- The protovalidate module loads in an idle callback, like its rule compilation (D10).
- The bottom banners leave their height to their ResizeObserver instead of a synchronous read in `attached()`.
- At most 20 long-animation-frame events per page load.
- Background Sync only for write RPCs (artist Create; Follow, Unfollow, SetHype); reads go straight to the network.
- The API's CORS handler sets `Access-Control-Max-Age: 7200`; without it every RPC method's first call per page load paid a preflight (three in series on the signed-in path).

Left out: onboarding guests' concert checks on every entry (required by "Concert check at page load uses List RPC"), and start-up items with wider impact (blocking user hydration, the Zitadel token chain, the router waiting for every route chunk, the `config.json` round trip, per-bubble sprites, blurs over the canvas, binary RPC encoding, the duplicate OTel span), which stay in frontend issue #782.

### 13. Cold-load time budget

The criterion in task 6.1 (first name within 300 ms of the first `ListSimilar` response) assumed the data arrives last. On v1.105.0 it arrives first: the first `ListSimilar` response comes at 3.8–4.6 s, the first bubble at 4.5–5.4 s, and the first name about 400 ms after the first bubble. The remaining time is app start-up, so the change adopts a budget measured where the fan waits (requirement "Cold load meets a time budget"):

| metric | budget (median) | v1.107.0 signed in | v1.107.0 guest |
|---|---|---|---|
| first name (`first_name_ms`) | ≤ 6.0 s signed in, ≤ 3.0 s guest | 5,008 ms | 1,745 ms (clean Chrome), 2,545 ms (container) |
| first bubble (`ghosts_ms`) | recorded, not bound | 2,996 ms | 1,260 ms / 1,788 ms |
| first bubble → first name | recorded, not bound | 1,975 ms | 485 ms / 724 ms |

How the budget settled (2026-10-19): the first plan bound the first bubble (≤ 1,000 ms), the first name (≤ 1,500 ms) and first bubble → first name (≤ 500 ms). The first two could not be met without the designs the owner declined (below). The third was then kept alone, but it is the wrong measure: v1.107.0 drew ghosts about 1.8 s sooner, and the same data then arrived later relative to them, so the bound grew worse as the fan waited less. The budget is therefore the first name from the page start, set at the v1.107.0 medians with margin as a regression bound. The signed-in path still waits 1.1–2.0 s between the follow list answer and the first `ListSimilar` send on the client; that is tracked in frontend#801.


Reference setup: desktop Chrome, device emulation at 375 px, DevTools "Slow 4G" network throttling and 4x CPU throttling (the Lighthouse mobile profile), HTTP cache on, repeat visit, about 10 loads each for a signed-in fan with follows and a guest. A first visit is reported but not budgeted: it is bound by the network. The owner's manual runs already used "Slow 4G" (the `pannpers.dev` Chrome profile stores `active-network-condition-key: SPEED_SLOW_4G`), which is why they took about twice as long as the CPU-only traces.

Under the first plan: "Slow 4G" adds about 0.56 s of latency to every request, so the budget dictated the network on the critical path: no request before the first bubble (first bubble ≤ 1,000 ms), and at most one round trip before the first name (≤ 1,500 ms). A guest's `ListTop` can be that one round trip if it starts during start-up. A signed-in fan needs two in series today (`FollowService/List`, then `ListSimilar`).

Where the time goes (profiled trace of v1.106.0 on the reference setup, signed in, task 7.1): the `config.json` round trip 0.6 → 2.0 s; Aurelia start-up and the first render on the main thread 2.0 → 3.6 s; ghosts at 3.6 s; `FollowService/List` done at 4.7 s; `ListSimilar` 4.9 → 5.7 s; first name at 5.9 s. With "Slow 4G" adding about 0.56 s to every request and 4x CPU stretching start-up, 1 s to the first bubble needs no request and almost no script before it.

Decided:

- **Done (7.2, 7.3a–d)**: ghosts before physics, one label measurement per string, `config.json` requested from `index.html`, rendering Discovery before user hydration, the initial load started during start-up.
- **`config.json` stale-while-revalidate (7.3e)**: the service worker serves the copy kept from the last start and refreshes it in the background, which removes the 1.4 s round trip on a repeat visit. A config change made without a release reaches a device one start later (accepted by the owner). Activating a new service worker deletes the kept copy, so a release always starts with the config read from the network.
- **Generic boot skeleton removed (7.3f)**: the rows in `index.html` only flashed before Discovery's ghosts. The owner is content with how fast ghosts appear and asked to drop the generic skeleton on every screen. The skeleton was also the only feedback on the sign-in callback, which finishes the sign-in in `canLoad` before anything renders (prod log: 1 to 4.5 s from the callback page to `UserService/Get`). That screen gets a static spinner in `index.html`, shown only on `/auth/callback`.
- **Not done: static ghosts in `index.html`** (ghosts drawn before Aurelia starts). The owner is content with the ghost timing.
- **Not done: a saved field** (the last shown artists kept and redrawn at start). It would add a second source of truth for the field and its own invalidation and tests; the owner declined it for testability and maintainability.
- **Deferred: lazy route components.** Aurelia 2.0.0-rc.2 loads every `component: import()` in the route table eagerly and the router's `allResolved` waits for all of them; the `() => import()` form exists only in the 2.1 docs. It is revisited with the Aurelia 2.1 upgrade instead of a custom loader.
- **Not done: binary RPC encoding.** `ListTop` is about 20 KB of JSON, and the E2E tests mock JSON responses.

@spec-manual components/infrastructure/fan/web/route/discovery "Signed-in fan with followed artists" -- the owner's reference-setup procedure (task 7.x), medians of `perf.discovery_reveal` in PostHog, recorded under "Measurements"
@spec-manual components/infrastructure/fan/web/route/discovery "Guest" -- the same procedure as a guest, or the container A/B of release builds with the same throttling, recorded under "Measurements"

## Risks / Trade-offs

- **Bubbles appear in arrival order.** Ghost slots are reused in arrival order, not seed order, so where a given artist appears differs from today. The final membership and order are unchanged, and positions were already random.
- **The concurrent `ListTop` can delay a seed.** On a backend cache miss it can take a throttler slot ahead of a seed by up to 200 ms. Mitigation: at most once per country per 6 h, and the fan sees the first seed's names well before then.
- **A 50-artist lookup registers more new artists.** A first lookup can create up to 50 new artists instead of 10, each announced and followed by name resolution and image sync in the event consumer. Mitigation: these steps are asynchronous and the volume is small. The first ListSimilar response takes slightly longer only when many returned artists are new.
- **Narrowing the `ListSimilar` limit is breaking for an external caller.** Mitigation: there is none outside the fan web. Mark the specification PR with the `buf skip breaking` label if buf flags it.
- **6 h staleness.** Search results and charts can be up to 6 h old. This is accepted for catalog data.
- **No trace-based proof of Decision 4.** Mitigation: Decision 5 ships first. If `first_name_ms − ghosts_ms` stays high after Decision 1, the per-frame cost is confirmed, and the sprite step follows.

## Migration Plan

1. **Frontend, measurement first.** Decision 5 ships alone, then about 10 owner cold loads per path on a phone are recorded as the baseline, in this design under "Measurements".
2. **Specification.** The proto `lte: 50` change, then a Release, then BSR gen.
3. **Backend.** Decision 6, after BSR gen, with the dependency bump.
4. **Frontend, optimizations.** Decisions 1–4 and 7–9. These do not depend on the proto change; the fan web already requests at most 50.
5. **Re-measure** with the same device and procedure, and record it under "Measurements".

Rollback: each repository's PR reverts on its own. Reverting the backend keeps working with the narrowed proto.

## Measurements

<!-- Filled during apply: medians of ghosts_ms, first_name_ms, all_names_ms per path and entry, before and after. -->

Device and procedure: PC Chrome with DevTools device emulation at a 375 px viewport (reported as Mobile Safari) and CPU throttling, "Disable cache" off, reloading `/discovery` so every load is a cold visit with `entry = page_load`. The after run uses the same settings. Source: PostHog `perf.discovery_reveal`, project liverty-music-prod.

**Before (v1.98.0, 2026-10-17)**

| path | entry | n | ghosts_ms | first_name_ms | all_names_ms | first_name − ghosts |
|---|---|---|---|---|---|---|
| top | page_load | 7 | 7247 (5754–11137) | 10246 (7667–13810) | 10248 (7669–13810) | 2110 |
| seed_similar | page_load | 1 | 16277 | 18919 | 18920 | 2642 |

Medians, with the range in parentheses. The `seed_similar` row is a single load, not yet a baseline. One earlier `top` event (03:37 UTC, before the procedure was fixed) is excluded.

This run is superseded: signed-in loads took the `top` path (follows were not loaded), and 4 of 6 later loads sent no event (artists drawn before any ghost, inferred from the code, not confirmed). The baseline is recorded again on the release that fixes both.

**Before, recorded again (v1.98.1, 2026-10-17)**

| path | entry | n | ghosts_ms | first_name_ms | all_names_ms | first_name − ghosts |
|---|---|---|---|---|---|---|
| seed_similar (signed in, 5 seeds) | page_load | 7 | 6276 (4698–10177) | 10668 (9384–20221) | 10669 (9385–20223) | 4392 (3739–10044) |
| top (guest) | page_load | 5 | 3464 (2910–8606) | 4152 (3538–11991) | 4153 (3539–11993) | 818 (628–3385) |

On v1.98.1 every signed-in load took the `seed_similar` path, and the reveal events matched the Discovery page loads (7 events for about 6 `$opt_in` page loads in the same minutes). `all_names_ms` is 1–2 ms after `first_name_ms`: every name appears at once. The guest boots about 3 s faster to the first bubble than the signed-in fan (3464 vs 6276 ms), outside the scope of this change. One guest `in_app` load (693 / 1459 / 1460 ms, right after the sign-out navigation) is excluded.

**After (frontend v1.99.0 and backend v1.88.0 in production, 2026-10-18 00:02–00:04 UTC, same device and settings)**

| path | entry | n | ghosts_ms | first_name_ms | all_names_ms | first_name − ghosts |
|---|---|---|---|---|---|---|
| seed_similar (signed in, 5 seeds) | page_load | 6 | 7035 (5169–12391) | 13605 (8325–18128) | 14352 (8572–18340) | 4212 (2871–10026) |
| top (guest) | page_load | — | — | — | — | — |

The progressive reveal is visible: `all_names_ms` now trails `first_name_ms` by 1–1669 ms (median 398), where before it trailed by 1–2 ms. The backend cache works: from the second load on, repeated seeds answer `ListSimilar` in 0 ms (fan-api access log, e.g. 4 of 5 seeds at 00:03:09).

The first name did not come sooner. Aligning each event (`all_names_ms` back from the capture time) with the fan-api access log for the same User-Agent shows that the client, not the server, now dominates:

| median | before | after |
|---|---|---|
| `FollowService/List` response → first `ListSimilar` sent | 1817 ms | about 3550 ms (1.9–5.3 s) |
| data needed for the first name → first name drawn | 1981 ms (from the last seed response: all at once) | about 2400 ms (from the first seed response; 1.0–5.7 s) |

Drawing a revealed name needs about 250 ms of real time, so seconds of delay after a response mean the main thread is busy; the 6.1 bound (`first_name − ghosts` ≤ first `ListSimilar` response + 300 ms) fails on all 6 loads. Which work holds the main thread (the per-frame ghost and bubble drawing with gradients and `shadowBlur`, or module evaluation such as the earlier physics engine download) is not known: no performance trace was taken. Times compare a client clock with the server clock, so each figure carries the clock offset (about ±100 ms).

A guest run driven by Playwright in the pinned container (iPhone SE emulation, CPU throttling 4x and 6x, 10 loads each, timings read from the performance marks) gave ghosts 1419 / 1637 ms, first name 2251 / 2458 ms and first name − ghosts 793 / 796 ms. It is not comparable with the guest baseline, which was taken in the owner's Chrome, and these events did not reach PostHog (presumably dropped as automated traffic).

**Traces of the main-thread fixes (2026-10-19, owner's Chrome driven over CDP, GPU, 375 px, 4x CPU throttling, V8 CPU profile; one signed-in cold load each, so a direction, not a median)**

| release | `List` finished → `ListSimilar` sent | first bubble | first name | main-thread work in that gap |
|---|---|---|---|---|
| v1.99.0 | 4.3 s | 16.6 s | 32.5 s | 3.3 s microtask (CEL rule compilation; found with the profiler in a repeat trace) |
| v1.102.0 (D4 amendment, D10) | 2.0 s | 6.8 s | 10.7 s | 1.3 s PostHog queue replay |
| v1.103.0 (D11) | 0.7 s | 6.1 s | 8.5 s | no long task |

`measureText` in the reveal window: 586 ms (v1.99.0, per spawn frame), then 318–451 ms (one layout per bubble). The service worker was ruled out: it resolved `FollowService/List` 383 ms after sending it, and the page handled the response only after a 4 s microtask ended. The remaining boot cost (template compilation, forced layout in `attached()`, `showPopover`) is tracked in frontend issue #782.

**After, recorded again (frontend v1.103.0, backend v1.89.0, 2026-10-19 00:50–00:59 UTC, owner's manual procedure as before)**

| path | entry | n | ghosts_ms | first_name_ms | all_names_ms | first_name − ghosts |
|---|---|---|---|---|---|---|
| seed_similar (signed in, 5 seeds) | page_load | 9 | 4686 (3553–9717) | 6521 (5190–12214) | 7022 (5344–13069) | 1737 (1521–3980) |

Against the before (seed_similar, n = 7): first name 10668 → 6521 ms (−39%), first name − ghosts 4392 → 1737 ms (−60%), first bubble 6276 → 4686 ms (−25%). One `in_app` load is excluded.

Aligned with the fan-api access log: `FollowService/List` finished → first `ListSimilar` sent, median 1817 → 1031 ms; the data a first name needs → first name drawn, 1981 ms (last seed response, all at once) → 1070 ms (first seed response). The 6.1 bound (first name − ghosts ≤ first `ListSimilar` response + 300 ms) still fails on all 9 loads: about 1 s passes between the first response and the first name, where the fade itself needs about 250 ms. The first bubble still takes 4.7 s of app start-up, which this change does not address (issue #782).

**Guest A/B (2026-10-19)**: the guest after was not recorded by hand. Instead both frontend builds ran in the same harness: the pinned Playwright container (iPhone SE emulation, 4x CPU throttling, no GPU), the app's HTML and JS served from local builds of v1.98.1 and v1.103.0 by request interception, the API and `config.json` from production, the service worker and PostHog blocked, 10 rounds alternating the order, timings from the performance marks. Absolute times are lower than in the owner's Chrome (no network for assets).

| build | n | ghosts_ms | first_name_ms | first_name − ghosts |
|---|---|---|---|---|
| v1.98.1 (before) | 10 | 919 (853–1254) | 1660 (1430–2068) | 741 |
| v1.103.0 (after) | 10 | 909 (832–1127) | 1473 (1292–1787) | 521 |

Paired by round, the first name came sooner in 9 of 10 rounds (median −191 ms).

**After, v1.105.0 (frontend) and v1.90.0 (backend), 2026-10-19 05:10 UTC, owner's procedure, signed in**

| path | entry | n | ghosts_ms | first_name_ms | all_names_ms | first_name − ghosts |
|---|---|---|---|---|---|---|
| seed_similar (signed in, 5 seeds) | page_load | 4 | 5009 (4544–5358) | 5481 (4824–5799) | 6360 (5076–6928) | 406 (280–574) |

One more load (24,526 ms to the first bubble) was the first after the release and downloaded the new code; it is excluded. Against the before: first name 10,668 → 5,481 ms (−49%), first bubble → first name 4,392 → 406 ms. In the fan-api log, `FollowService/List` now runs during start-up next to `UserService/Get` (about 2.6 s), and the first `ListSimilar` answers at 3.8–4.6 s, before the first bubble (4.5–5.4 s): the data no longer holds the reveal back. The old 6.1 bound (first name ≤ first `ListSimilar` response + 300 ms) is therefore replaced by the cold-load budget (D13).

**After, v1.107.0 (frontend), 2026-10-19 09:40 UTC, guest, reference setup (Playwright in the pinned container against production: iPhone SE viewport, Slow 4G and 4x CPU through CDP, service worker on, repeat visits, PostHog blocked)**

| path | n | ghosts_ms | first_name_ms | first_name − ghosts |
|---|---|---|---|---|
| top (guest, no follows) | 10 | 1788 (1657–1954) | 2545 (2364–2846) | 724 (690–979) |

Against v1.106.0 the first bubble moved from about 3.6 s (trace) to 1.8 s: `config.json` now comes from the kept copy (4 ms). This missed the first bound of 500 ms, so the guest bound became 800 ms (the owner agreed, 2026-10-19): a guest's `ListTop` is one Slow 4G round trip that ends about 500 ms after the ghosts, and the first frame with names adds about 250 ms at 4x. The signed-in bound stays at 500 ms, because a signed-in fan's data already arrives before the ghosts (v1.105.0 above). Trace of one load: `ListTop` is sent at 1,412 ms and finishes at 2,301 ms (one Slow 4G round trip), 513 ms after the ghosts at 1,788 ms; then 89 ms to decode it and one 235 ms frame (83 ms of `fillText`) to the first name at 2,570 ms. Moving the start-up load from `AppTask.activating` to `AppTask.creating` did not move the `ListTop` send (A/B of 10 rounds, both about 1,150 ms with the config served locally), so it was not shipped.

**After, v1.107.0, 2026-10-19 11:00 UTC, owner's account, clean Chrome on the owner's PC (separate profile, no extensions, CDP on port 9223; iPhone SE emulation, Slow 4G and 4x CPU through CDP; repeat visits)**

| path | n | ghosts_ms | first_name_ms | first_name − ghosts |
|---|---|---|---|---|
| seed_similar (signed in, 5 seeds) | 10 | 2996 (2785–3457) | 5008 (4473–6011) | 1975 (1599–2683) |
| top (guest, new context of the same Chrome) | 10 | 1260 (1056–1430) | 1745 (1597–1994) | 485 |

Two runs earlier the same day are excluded as measurement errors. In the owner's everyday Chrome, extensions (Adblock Plus, Claude in Chrome) ran content scripts in the page; in both Chromes, another `liverty-music.app` tab of the same profile (the dashboard) shared the renderer with the measured page under 4x throttling, which put the first bubble at 7.8–9.3 s. With that tab on `about:blank` the first bubble came at 1.5–3.5 s. Signed-in loads: `UserService/Get` and `FollowService/List` start at about 1.0–2.5 s and answer at 1.6–2.7 s, and the first `ListSimilar` is sent 1.1–2.0 s after the follow list answered (median 3,888 ms) and answers at 4,492 ms.
