## Context

See proposal.md for why. This design records what a spike on 2026-11-07/08 measured, and the decisions taken from it.

**Code today.** The bubble field is one `<canvas>` in `dna-orb-canvas` (shadow DOM), drawn every animation frame by `DnaOrbCanvas.loop` (`frontend/src/components/dna-orb/dna-orb-canvas.ts:586`):

- Physics: Matter.js steps by a capped delta (`bubble-physics.ts:445`). The engine has gravity `y: 0.15` (`bubble-physics.ts:113`), so the bubbles settle into a pile, but every frame still tests and resolves all resting contacts.
- Bubbles: `renderBubble` draws a radial gradient, the label through a cached layout, and a rim whose `shadowBlur` is `r × 0.35`, for every bubble on every frame (`dna-orb-canvas.ts:696`, rim at `:780`).
- Canvas size: `render()` calls `getBoundingClientRect()` every frame (`dna-orb-canvas.ts:629`).
- Tap: the 30 similar artists a tap adds are spawned at the tap point in one call (`bubble-physics.ts:333`, `spawnBubblesAt`), and the 29 oldest fade out while they still collide.
- Absorption: the bubble flying to the orb draws its name with `fillText` in a font whose size changes every frame (`absorption-animator.ts`, `render`).
- Sound: the first tap creates the `AudioContext` and the noise buffer (`audio-engine.ts:274`, `ensureContext`; `ensureNoiseBuffer`).

**Measurement setups used.**

- **Frame reference setup** (the spec's): desktop Chrome with GPU rendering, 412 px viewport, 4x CPU throttling, a guest field of 50 artists. The spike ran it on the owner's Windows Chrome 156 (Intel integrated GPU), with the throttling sent over the DevTools protocol. A probe script injected into the production build mocked the network and measured rAF intervals, script time per frame, and long animation frames.
- **Emulated-GPU setup**: Playwright Chromium in WSL with SwiftShader. GPU work runs on the CPU there, so frame rates in this setup are much lower and noisy. It was used only to split main-thread time by category (CPU profiles and traces).
- **Network and log level**: the dev `config.json` sets `logLevel: debug`; production sets `info` (`cloud-provisioning/k8s/namespaces/frontend/overlays/prod/fan-web-configmap.yaml:43`). Debug logging added 80–200 ms to a tap in the spike's first profiles, so every measurement here serves the config with `logLevel: info`.

**Spike results** (frame reference setup, 50 bubbles, 4 runs each; spike commits in `frontend/.claude/worktrees/sprite-spike`, scripts in `~/.cache/html-in-canvas-spike/`):

| | production build | after this design |
|---|---|---|
| idle, frames per second | 49–59 | 60 |
| idle, 95th-percentile interval | 16.8–33.4 ms | 16.8 ms |
| idle, script per frame (median) | 3.1–4.5 ms | 1.9–2.0 ms |
| after a tap, frames per second | 36–39 | 54–55 |
| after a tap, longest frame | 317–367 ms | 84–134 ms |
| after a tap, frames over 50 ms | 2–6 | 2–4 |

A guest cold load in the emulated-GPU setup drew the first name at 4.95–5.17 s with the production build and 4.28–4.68 s after the changes. That setup has no network delay and is not the spec's cold-load reference setup.

**Baseline with the ported harness** (task 1.1, 2026-11-08; `frontend/scripts/measure-discovery-frames.ts` over CDP in the owner's Windows Chrome 156, Intel integrated GPU; device emulation 412 × 915 at DPR 2, 4x CPU throttling, 5 runs, no tracing). DPR 2 is the canvas cap and draws more pixels than the spike's native DPR 1.5, so these are not comparable with the spike table above.

| `main` (df0c5ba8), median of 5 runs | value | bound |
|---|---|---|
| idle, median interval | 16.7 ms (runs: 33.1, 16.7, 16.8, 16.7, 16.7) | 17 ms |
| idle, 95th-percentile interval | 33.5 ms | 34 ms |
| idle, script per frame (median) | 15.5 ms | |
| idle, `getBoundingClientRect` calls in 6 s | 199–217 | |
| after a tap, longest frame | 517 ms (484–684) | 200 ms |
| after a tap, frames over 50 ms | 8 (6–9) | 5 |

Idle trace (`--trace`, medians of 5 runs on `main`): 33 layouts, 33 style recalculations and 67 paints per second.

**Branch results so far** (same setup, branch at frontend 98a4ffcc):

- Frames, 5 runs without tracing: idle median interval 16.7 ms, 95th percentile 16.8 ms, script per frame 4.4 ms, no `getBoundingClientRect` call (task 3.3); after a tap, frames over 50 ms 3 (3–4), longest frame **250 ms (217–384), over the 200 ms bound**.
- The longest frame after a tap is not Discovery code: its long-animation-frame attribution is an `IdleRequestCallback` of 176–246 ms from the `main` chunk, the request validator compiling the `ListSimilar` rules the first time the tap sends that request (`frontend/src/services/validate-interceptor.ts`, `scheduleIdle`). Open question below.
- `audio.prepare()` (D7) takes 197 ms in one idle callback at 4x. It runs within 1 s of attach, before the first tap, as D7 intends.
- Idle trace (tasks 4.1, 4.2): 0 layouts and 0 paints per second, against 33 and 67 on `main`; about 45 style recalculations per second remain, with no layout or paint after them.
- Look (task 2.6): `--stills` draws the field from fixed inputs (20 bubbles sorted by name, fixed radii and grid positions, orb layers hidden) in both builds. The direct draw matches `main` to 2/255. With sprites, the names are pixel for pixel the same; 1.3% of pixels differ by more than 8/255, all on the faint rim ring, which the sprite paints under the name instead of over it. The absorbing bubble shows its own wrapped label shrinking instead of a one-line name squeezed to fit, as D6 states. In one of three branch runs the direct draw differed from `main` by a sub-pixel change in the name glyphs; the other two matched exactly.
- Guest journey (task 7.2, production build of frontend 74639558 in Playwright's Chromium, 412 px, with and without reduced motion): a cold load until every bubble shows a name, three bubble taps (each absorbed, the field refilled), a search and follow, and a switch to All Nearby and back all completed with no console error and no page error, the same as `main`. The Chromium projects of the existing Discovery-related functional E2E specs pass (88 passed, 5 skipped); their `webkit-shell` project cannot start WebKit in this WSL (missing system libraries) and ran in the CI of frontend#963: 458 passed, 1 flaky (an organizer sales-tab test that passed on retry), including `webkit-shell`, `webkit-repro` and `webkit-organizer-guide`.
- Frames after D11, 2026-11-08 13:23 on AC power with the other local session paused: the machine ran about 2.5 times slower than in the morning (`main` script per idle frame 39.3 ms against 15.5 ms), so these runs do not judge the bounds. Under the same conditions the branch cut the idle script per frame from 39.3 to 11.2 ms, the idle 95th-percentile interval from 83.5 to 34.2 ms and the longest frame after a tap from 568 to 267 ms. Task 7.1 waits for a run on a machine in the morning's state.
- **Frame bounds (task 7.1), 2026-11-08 19:28, on AC power, the other local session paused (load average 0.04–0.20).** Same frame reference setup (Windows Chrome 156 over CDP, Intel integrated GPU, 412 × 915 at DPR 2, 4x CPU, guest field of 50), 5 runs each, no tracing:

  | | `main` (frontend 1811936e) | branch (frontend ac97c305) | bound |
  |---|---|---|---|
  | idle, median interval | 16.7 ms | 16.7 ms | 17 ms |
  | idle, 95th-percentile interval | 33.4 ms | 16.9 ms | 34 ms |
  | idle, script per frame (median) | 13.1 ms | 2.9 ms | |
  | after a tap, longest frame | 367 ms (367–434) | 83 ms (18–84) | 200 ms |
  | after a tap, frames over 50 ms | 8 (6–10) | 2 (0–2) | 5 |

  Every bound of "Idle field of 50 bubbles" and "Tap on a bubble in a field of 50" holds on the branch; `main` misses both tap bounds. No console error in any run.
- There are no visual baselines for the `discovery-swap-button` and `onboarding-progress` stories (animated elements are not screenshot-tested), so tasks 4.1 and 4.2 changed none; their stories pass in both storybook projects.
- **Production after the release, read 2026-11-09.** frontend v1.146.0 reached production at 00:37 JST. Up to 00:46 only one tester's device sent events: a Pixel 8 Pro, Chrome 156 for Android, the installed app (`display_mode: standalone`). There is no iPhone test device, so iPhone Safari has no figures after the release; they come only from real fans' events.

  `perf.discovery_frames`, 8 visits of 86–2,382 frames each, 30 or 50 bubbles, names painted in the worker on every visit. Medians across the visits:

  | Chrome, Android (Pixel 8 Pro) | median | range |
  |---|---|---|
  | median interval | 16.7 ms | 16.7–25.0 ms |
  | 95th-percentile interval | 20.9 ms | 16.8–75.1 ms |
  | longest frame | 159 ms | 108–292 ms |
  | frames over 50 ms | 5 | 4–7 |

  The last two visits ran at 25 ms (40 frames per second) from the first frame, which points to the phone lowering its refresh rate rather than to the page. Even the shortest visits (86 frames) have 4–5 frames over 50 ms, so those frames come at the start of a visit, not from a steady field.

  `perf.long_animation_frame` on Discovery, next to proposal.md's figures (the event reports only frames of 100 ms or more, at most 20 per page load):

  | | before the release (30 days) | after the release |
  |---|---|---|
  | Chrome, Pixel 8 Pro | 2,942 frames, median 132 ms, 90th percentile 146 ms, longest 454 ms | 9 frames, median 148 ms, 90th percentile 165 ms, longest 167 ms |
  | Mobile Safari, iPhone | 2,885 frames, median 177 ms, 90th percentile 693 ms, longest 7,811 ms | no test device |

  The long-frame medians cannot compare the two periods: they are medians of frames already over 100 ms, and nine frames from one evening are too few. The longest frame fell from 454 to 167 ms on this phone.

  `perf.discovery_reveal` sent one event after the release, a `page_load` from the same phone with 296 s to the ghosts. That is the installed app resumed from the background, measured from its navigation start, not a slow reveal. The same happened before this change (4,458 s on 2026-10-19, 46,971 s on 2026-11-03), so the reveal event needs to skip a visit whose page was hidden before the reveal; that is outside this change.

## Goals / Non-Goals

**Goals:**

- Meet the frame bounds in "Physics-Based Bubble Animation" without changing how a bubble looks or how the field behaves.
- Keep "Revealed bubble names fade in on real time" and the cold-load budget.
- Ship a production signal (the frame-timing event) to confirm the effect on phones, since the owner has no iPhone and dev is stopped.

**Non-Goals:**

- Discovery's look, the orb effects, the sounds.
- The dashboard's timetable render bounds (`meet-timetable-render-budget`).
- A WebGL renderer (D1).

## Decisions

### D1. Paint each bubble once into sprites; reject per-frame text, HTML-in-Canvas and WebGL

**Decision.** A bubble's body (gradient + soft rim) and its name are each painted once into a sprite keyed by look and full radius, and every frame pastes them with `drawImage`, scaled during spawn.

**Why.** On the frame reference setup the production build idles at 29–59 frames per second, while its script time per frame is only 3–5 ms. The cost is the per-frame `shadowBlur` raster for 50 rims, not JavaScript.

**Measured alternatives:**

- **Per-frame text, with a shared rim sprite and cached gradients.** This needs no sprites for names and no worker. It had 3.6–5.0 ms script per frame against 2.1–2.6 ms with name sprites, 32–57 frames per second after a tap against 56–60, and one 884 ms frame. Drawing 50 names 60 times a second costs more than painting each name once. A web font would not change this, and a Japanese web font adds megabytes to the start-up. Labels keep `system-ui`.
- **HTML-in-Canvas** (Chrome 157). With the feature flag on Chromium 156 in the emulated-GPU setup, 50 drawable elements took about 250 ms per frame against about 158 ms for the current canvas. No source states support in Safari, and iPhone Safari sent 88% of Discovery reveal events.
- **WebGL.** It was the fastest in the isolated benchmark (33 ms per frame emulated). But it needs a second renderer for the ground glow and light rays under the bubbles, plus context-loss handling and a 2D fallback. Sprites met the bound without it.

**Not measured.** DOM text for names. Moving 50 elements every frame recalculates style every frame, the cost the HTML-in-Canvas post itself warns about (developer.chrome.com/blog/html-in-canvas: per-frame `style.transform` updates make the browser recalculate style before each frame).

### D2. Sprites are painted in a Web Worker; the frame never waits for one

**Decision.**

- A module worker (`sprite-worker.ts`) paints sprites into an `OffscreenCanvas` and returns `ImageBitmap`s, 4 at a time.
- The canvas starts the worker in `attached()`, so the module loads before the artists arrive, and terminates it in `detaching()`. It requests the sprites of every bubble on, or queued for, the field whenever the field changes.
- The pure paint and layout code (`computeLabelLayout`, `wrapText`, the body painter) moves to a module with no Aurelia import (`sprite-paint.ts`), shared by the worker and the main thread.
- Until a sprite arrives, a full-size bubble (a ghost turning into an artist, `scale >= 1`) is drawn directly, as today, with the same paint code. A bubble popping from a tap starts tiny and waits for its sprite.
- Where `OffscreenCanvas` 2D or module workers are missing, the canvas paints sprites on the main thread, at most 4 new ones per frame.

**Why off the main thread.** A name sprite costs about 13 ms at 4x in the emulated-GPU setup (canvas creation, layout, `fillText`). 30 bubbles after a tap are about 400 ms of work. Both alternatives left it in the frames:

- At most 4 per frame on the main thread still gave 116–190 ms script per frame after a tap.
- `requestIdleCallback` never ran: a running animation leaves no idle time at 4x.

The worker cut the 95th-percentile script per frame after a tap to 41–73 ms (emulated-GPU setup).

**Why the direct draw.** A cold load requests 100 sprites at once. They arrived 315–423 ms (median) after the request, longer than the spec's 300 ms name bound, so the name cannot wait for them. Drawing tap-spawned bubbles directly as well raised the frames over 50 ms after a tap from 2 to 4–6 on the frame reference setup, so the direct draw is limited to full-size bubbles.

**Reveal marks.** `RevealMarks` (`reveal-marks.ts`) decides a name is shown from the bubble's opacity. It moves to the frame that actually drew the name, from a sprite or directly, as "Revealed bubble names fade in on real time" now states.

### D3. Matter.js sleeping, woken on every field change

**Decision.**

- `Engine.create({ enableSleeping: true })`.
- `BubblePhysics` wakes every body (`Sleeping.set(body, false)`) whenever bodies are added, removed or start fading out, a queued spawn enters, or the walls are rebuilt on resize.

**Why wake all.** Matter wakes a sleeper only when it collides with a moving body (`Sleeping.afterCollisions` in matter-js 0.20 `src/core/Sleeping.js`, read in `frontend/node_modules/matter-js`). A body that loses its support from below would otherwise float in place.

**Effect.** Idle script per frame fell from 4.6–5.9 ms to 1.8–2.0 ms. With sleeping removed from the otherwise final build, the longest frame after a tap was 117–183 ms, against 67–150 ms with it.

**Alternatives.** Fewer solver iterations, or a 30 Hz fixed physics step. Not needed for the bound, and both change how the bubbles feel.

### D4. A tap's top-up enters gradually and fading bubbles stop colliding

**Decision.**

- Tap-origin placements go into a queue. 3 enter per frame, each with its own random outward push.
- A fading-out body gets `collisionFilter.mask = 0`, restored if it is revived.

**Why.** 30 overlapping circles on one point, with 29 still-colliding fading bodies, made the solver's worst frames. Together with D5 and D6, this cut the longest frame after a tap from 1.4–2.1 s to 0.2–0.37 s (emulated-GPU setup).

**Effect on the look.** At 60 frames per second the 30 bubbles leave over about 170 ms instead of in one frame. The tap feedback order in "Bubble Burst On Tap" is unchanged.

### D5. The canvas size is cached on resize

`sizeCanvas()` already reads the rect on every resize, through the existing `ResizeObserver`. It stores the width and height, and `render()` uses them instead of calling `getBoundingClientRect()` each frame. That per-frame read cost 113 ms over 3 s after a tap at 4x, because DOM changes forced a layout inside the frame.

### D6. The absorbing bubble pastes its name sprite

`AbsorptionAnimator` gets a `drawLabel` callback from the canvas, which pastes the tapped bubble's name sprite scaled to the shrinking radius. When no sprite is available, it falls back to today's `fillText`.

The per-frame font change cost 196 ms over 3 s at 4x. The name now shrinks as an image of the bubble's own label instead of a re-laid-out line: the same text and font as before the tap, scaled.

### D7. The audio graph is built within 1 s of attach

**Decision.** `IAudioEngine` gains `prepare()`, which creates the `AudioContext` (suspended until the tap's `unlock()` resumes it) and the noise buffer. The canvas calls it with `requestIdleCallback(…, { timeout: 1000 })`, or `setTimeout(…, 1000)` where idle callbacks are missing, and cancels it in `detaching()`.

**Why.** It moved about 100 ms (at 4x) out of the first tap's handler. A context created before a user gesture starts in the `suspended` state and `resume()` inside a gesture starts it (MDN, "Autoplay guide for media and Web Audio APIs"; Chrome's autoplay policy, developer.chrome.com/blog/autoplay). Neither source states this for every Safari version; the frame reference setup checks Chrome, and task 7.2 does not cover iOS, so a Safari failure would show as no tap sound until the tap's `unlock()`, which still creates the context when `prepare()` did not. `unlock()` stays in the tap.

### D8. Decorative CSS animations on the compositor only

**Findings.** Stopping all three running animations removed 4–5 ms of layout, 2.3 ms of style and about 5 ms of paint per idle frame (emulated-GPU setup). Stopping them one at a time showed:

- **`swap-twinkle`** (`discovery-swap-button.css:132`). It animates `transform` on SVG `<path>` elements with `transform-box: view-box`, which Chrome lays out again every frame. It caused the layout and most of the style cost.
- **`progress-sheen`** (`onboarding-progress.css:114`). It animates `background-position`, which repaints every frame.
- **`starfield-twinkle`**. It animates `opacity`, which already runs on the compositor.

**Decision.**

- The three sparkles become HTML elements over the tile's SVG (a star shape by `clip-path` or a mask), animated by `transform` and `opacity`.
- The sheen becomes a pseudo-element band moved by `transform: translateX` inside the fill's `overflow: clip`.
- Both keep their timing, delays and reduced-motion rules. The tile still draws three bubbles with small sparkles, as "Swap tile switches between the artist bubbles and the All Nearby view" requires. Their stories get updated visual baselines.

### D9. The frame-timing event

**Decision.** A new analytics event `perf.discovery_frames` (in `analytics-events.ts`) with these properties:

- `frames`, `interval_p50_ms`, `interval_p95_ms`, `longest_ms`, `over_50ms` (frame counts and intervals)
- `bubbles` (the bubble count when the visit ended)
- `names_off_main_thread` (boolean)
- `display_mode`, added by the analytics surface

**Measurement.** The canvas records rAF intervals only while the loop runs (paused time is excluded by construction) and keeps the samples in a bounded array (at most 3,600, about one minute at 60 frames per second; later samples are dropped).

**When it is sent.** Once per visit, on `detaching` or on the first `visibilitychange` to hidden (listener added in `attached()`, removed in `detaching()`), when the visit has at least 30 samples. A switch to the All Nearby view ends the visit's measurement.

**Why not the existing event.** `perf.long_animation_frame` stops at 20 per page load and drops frames under 100 ms, so it cannot compare a typical frame before and after.

### D10. Start-up (frontend #782): trace, then fix per item

**Starting point.** Issue #782 (open) lists costs from a 2026-10-19 trace:

- Aurelia template compilation 1–3 s at 4x
- forced layout in `DnaOrbCanvas.initWhenSized` (234 ms) and the banners' `publishHeight` (126 ms)
- `showPopover()` on attach (193 ms)
- PostHog init (about 0.4 s)

Several things changed since: the queue replay drains in idle slices, and `config.json` is served stale-while-revalidate.

**Decision.**

1. Re-take signed-in and guest cold-load traces of `/discovery` and `/dashboard` on the spec's cold-load reference setup.
2. For each item over 50 ms before the first route paints, either remove it (a forced layout read whose value a `ResizeObserver` already has, a popover opened before it is needed) or defer it until after the first paint (components not visible at first paint), and record the before and after per item in this design.

**Not decided here.** Build-time template compilation. `@aurelia/vite-plugin` on `2.0.0-rc.2` has none, so cutting compile cost means fewer or later templates on the boot path, decided from the trace.

**Overlap.** `meet-timetable-render-budget` owns the timetable's render and its popover on attach. An item that change already removes is left to it.

**Traces (task 6.1, 2026-11-08).** `frontend/scripts/measure-cold-load.ts` on the branch build (frontend 74639558) with source maps, Playwright's Chromium in WSL, 375 px, DevTools' "Slow 4G", 4x CPU, repeat visit. The server mirrors the production Caddyfile: gzip, immutable `/assets/*`, `config.json` with `no-store`, other files with only `Last-Modified`. Without the compression and the heuristic caching the first visit's code was still downloading on the "repeat" load (a 317 KB uncompressed licenses chunk took 4.5 s), so earlier runs of the script measured the network, not the app. Each item below is a long animation frame that started before the first route paint (Discovery: the first bubble; Dashboard: the first contentful paint), attributed through the source maps, the trace's JavaScript stacks of forced layouts, and the CPU profile. 3 loads per case; first artist name 1.80 s (guest) and 1.76 s (signed-in).

| item | cost before first paint | cases | decision |
|---|---|---|---|
| Evaluating the `main` chunk: protobuf-es building the descriptors of every generated schema the RPC clients import (194 ms of self time in the profile), Aurelia's and i18next's module setup | 266–488 ms, every load | all four | Keep in this change. Deferring it means loading each route's RPC clients and schemas with the route, a restructuring of `src/adapter/rpc/` and the DI registrations; filed as frontend#962. |
| Starting the app once `config.json` arrives (`loadAppConfig` → Aurelia start): template compilation, the shell, the route's activation | 278–420 ms, including 54–81 ms of forced layout | all four | Keep the start; remove its forced layouts below. Build-time template compilation is not available (`@aurelia/vite-plugin` 2.0.0-rc.2). |
| Forced layout in `DnaOrbCanvas.attached`: `waitForSize` and `sizeCanvas` read `getBoundingClientRect()` while the route attaches | 38 + 20 ms in the frame above | Discovery | **Remove**: take the size from the `ResizeObserver` entry the canvas already observes, so the layout happens once, in the rendering step. |
| Forced layout in `DiscoveryRoute.loading` (`discovery-route.ts:246`) | 11–13 ms | Discovery | Below 50 ms; removed with the item above only if it is the same read. |
| Evaluating the chunks of routes not on screen (`event`, `tickets`, `dashboard`, …): the route table's `component: import(…)` starts every route's import when the shell module evaluates | 63–153 ms frames in about half of the loads | all four | **Defer**: load a route's module when it is navigated to, and import the others at idle after the first route has painted, so a later tab switch still finds them loaded. |
| Rendering the Dashboard after its RPC answers (`connect-transport` → the timetable) | 431–504 ms, including 55–69 ms of forced layout | signed-in Dashboard | Left to `meet-timetable-render-budget`, which owns the timetable's render. |
| Frames without script (HTML and CSS parsing, style) | 66–161 ms | all four | Keep: the document and the stylesheets. |

The banners' `publishHeight` and `showPopover()` on attach, listed in #782, do not appear among the forced layouts before Discovery's first bubble (checked in the Discovery traces only).

**Before and after per item (task 6.2, 2026-11-08 17:45, the other local session paused, load average under 1 at the start).** Same setup, 10 loads per build and fan, Discovery, medians:

| build | guest first name | guest long frames before the first bubble (sum) | signed-in first name | signed-in long frames (sum) |
|---|---|---|---|---|
| before (frontend 74639558) | 3119 ms | 2112 ms | 3288 ms | 2124 ms |
| canvas size read once (ebdf6e30) | 3171 ms | 2142 ms | 2637 ms | 1711 ms |
| off-tab routes imported when needed (c5b30dcb) | 2848 ms | 1758 ms | 2995 ms (2337–4097) | 1792 ms |

- Reading the canvas size once removes one forced layout of about 20 ms; the loads do not show it above their spread (the signed-in drop to 2637 ms is not repeated by the guest, which moved the other way).
- Importing off-tab routes when needed cut the guest's long frames before the first bubble by 383 ms and its first name by 323 ms. The signed-in loads spread from 2.3 to 4.1 s, so their median does not show the change.
- Both changes pass their unit tests and the Chromium projects of the functional E2E suite (425 passed). The suite's failures in that run also fail on `main` (`artist-filter-bar`, `deep-link-slow-device`) or changed from run to run (`organizer-first-come-editor`, `timetable-window`).

**Cold load meets a time budget (task 6.3).** Final build (c5b30dcb), the same 10 loads each:

| fan | first bubble (`ghosts_ms`) | first name (`first_name_ms`) | first bubble to first name | bound on first name |
|---|---|---|---|---|
| guest | 1903 ms | 2848 ms | 954 ms | 3.0 s |
| signed-in, 5 follows | 1926 ms | 2995 ms | 1046 ms | 6.0 s |

Both medians are within their bounds; the guest's by 152 ms. The same build measured 1.8 s at 14:20 the same day, so the machine's state moves these times by more than a second. Measured in Playwright's Chromium in WSL (the spec names desktop Chrome); the canvas draws through SwiftShader there, which lengthens the frames after the first bubble.

### D11. The requests of a bubble tap skip client-side validation

**Decision.** The request validator (`frontend/src/services/validate-interceptor.ts`) sends `ListSimilarRequest`, `FollowRequest` and `ListByArtistRequest` unvalidated (`UNVALIDATED_REQUEST_TYPES`), and never compiles their rules.

**Why.** The validator compiles a request type's rules in an idle callback the first time that type is sent. The tap sends the visit's first `ListSimilar`, so the compilation (176–246 ms in one callback at 4x) landed inside the 2.5 s after a tap and broke the 200 ms bound. These three requests are built only from ids the app holds, never from what the fan typed, so a rule they break is an app bug that the backend, validating every request with the same rules, reports anyway.

**Alternative.** Compiling Discovery's request types at idle after the reveal keeps the validation but only moves the same long frame into the idle field. Chosen by the owner on 2026-11-08.

## Risks / Trade-offs

- **[Numbers come from a laptop GPU, not a phone]** → The spec bounds use the frame reference setup. The frame-timing event (D9) gives the Pixel 8 Pro's numbers after release (recorded under Context). There is no iPhone test device, so iPhone Safari's numbers come only from real fans' events.
- **[Sprite memory]** → About 100 bitmaps of up to 144 × 144 px at 2x is about 8 MB. The cache is cleared above 400 entries, and when the device pixel ratio changes. Bitmaps of a cleared or detached cache are closed.
- **[A worker message lost or the worker failing]** → A missing sprite only means the bubble keeps its direct draw (full size) or stays invisible while tiny. If the worker posts an error, the canvas switches to the main-thread sprite path for the rest of the visit.
- **[Sleeping changes the feel]** → Bodies sleep only after Matter's motion threshold, so a settled pile looks the same. Any field change wakes everything.
- **[Staggered entry looks different]** → 170 ms at 60 frames per second, up to about 1 s at 10 frames per second. The bubbles still pop outward from the tap point.

## Migration Plan

Frontend only, one release. Rollback is the previous image. There is no data or API change.

## Open Questions

- Which #782 items the new traces show (D10). The task breakdown is per item found, under one task group.

## Scenarios verified by measurement

@spec-manual components/infrastructure/fan/web/route/discovery "Idle field of 50 bubbles" -- measured with `frontend/scripts/measure-discovery-frames.ts --cdp` on the frame reference setup (task 7.1, 2026-11-08 19:28, 5 runs, frontend ac97c305): median interval 16.7 ms, 95th percentile 16.9 ms. Frame rates depend on the GPU and the machine's load, so no CI test can hold the bound.
@spec-manual components/infrastructure/fan/web/route/discovery "Tap on a bubble in a field of 50" -- measured in the same task 7.1 runs: longest frame after a tap 83 ms, 2 frames over 50 ms.
@spec-manual components/infrastructure/fan/web/route/discovery "Realistic bubble physics" -- the field runs on Matter.js (`frontend/src/components/dna-orb/bubble-physics.ts`); the guest journey of task 7.2 and the task 7.1 runs showed the bubbles falling, settling and making room after a tap. Whether the motion looks natural is a judgement no automated test makes.
