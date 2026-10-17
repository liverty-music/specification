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

### 5. Report cold-load reveal timings, and ship that first

The canvas records:
- `performance.mark('discovery:ghosts')` when it first draws a ghost;
- `performance.mark('discovery:first-name')` when it first draws a label;
- `performance.mark('discovery:all-names')` on the first frame where every live bubble is real and past the label threshold.

It reports them to the route through a callback. The route sends one `perf.discovery_reveal` event (new `Events.DiscoveryReveal`, typed props in `analytics-events.ts`, following the existing `perf.*` events). Its properties are `entry`, `path`, `seed_count`, `ghosts_ms`, `first_name_ms` and `all_names_ms`:
- `entry`: `page_load` when Discovery is the document's first route, measured from `performance.timeOrigin`; `in_app` otherwise, measured from `performance.now()` at the route's `loading()`.
- `path`: `top` or `seed_similar`.

The route sends the event only when `prepareEntry` painted ghosts (a cold visit) and only if all three marks fire before `detaching`. The analytics service already applies consent and address sanitizing.

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
