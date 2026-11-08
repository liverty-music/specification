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

**Not measured.** DOM text for names. Moving 50 elements every frame recalculates style every frame, the cost the HTML-in-Canvas post itself warns about.

### D2. Sprites are painted in a Web Worker; the frame never waits for one

**Decision.**

- A module worker (`sprite-worker.ts`) paints sprites into an `OffscreenCanvas` and returns `ImageBitmap`s, 4 at a time.
- The canvas starts the worker in `attached()`, so the module loads before the artists arrive. It requests the sprites of every bubble on, or queued for, the field whenever the field changes.
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

**Why wake all.** Matter wakes a sleeper only when an awake body hits it. A body that loses its support from below would otherwise float in place.

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

**Decision.** `IAudioEngine` gains `prepare()`, which creates the `AudioContext` (suspended until the tap's `unlock()` resumes it) and the noise buffer. The canvas calls it with `requestIdleCallback(…, { timeout: 1000 })`, or `setTimeout(…, 1000)` where idle callbacks are missing.

**Why.** It moved about 100 ms (at 4x) out of the first tap's handler. Creating a context outside a gesture is allowed in Chrome and Safari; only `resume()` needs the gesture. `unlock()` stays in the tap.

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

**When it is sent.** Once per visit, on `detaching` or on the first `visibilitychange` to hidden, when the visit has at least 30 samples. A switch to the All Nearby view ends the visit's measurement.

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

## Risks / Trade-offs

- **[Numbers come from a laptop GPU, not a phone]** → The spec bounds use the frame reference setup. The frame-timing event (D9) gives the testers' iPhone and Pixel numbers after release. The owner can check on the Pixel 8 Pro.
- **[Sprite memory]** → About 100 bitmaps of up to 144 × 144 px at 2x is about 8 MB. The cache is cleared above 400 entries, and when the device pixel ratio changes. Bitmaps of a cleared or detached cache are closed.
- **[A worker message lost or the worker failing]** → A missing sprite only means the bubble keeps its direct draw (full size) or stays invisible while tiny. If the worker posts an error, the canvas switches to the main-thread sprite path for the rest of the visit.
- **[Sleeping changes the feel]** → Bodies sleep only after Matter's motion threshold, so a settled pile looks the same. Any field change wakes everything.
- **[Staggered entry looks different]** → 170 ms at 60 frames per second, up to about 1 s at 10 frames per second. The bubbles still pop outward from the tap point.

## Migration Plan

Frontend only, one release. Rollback is the previous image. There is no data or API change.

## Open Questions

- Which #782 items the new traces show (D10). The task breakdown is per item found, under one task group.
