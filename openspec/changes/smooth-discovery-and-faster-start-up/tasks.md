## 1. Frontend: baseline measurement

- [ ] 1.1 Port the spike's measurement harness into the frontend repository as a script under `scripts/` (production build served with the `config.json` log level set to `info`, network mocked, a guest field of 50 artists, Playwright at 412 px with 4x CPU throttling), with a README section on running it against Windows Chrome with a GPU over CDP; verify it prints the idle and after-tap frame metrics for the current `main` build, and record those numbers (about 5 runs) in design.md "Context"

## 2. Frontend: bubble sprites (design D1, D2)

- [ ] 2.1 Move `computeLabelLayout`, `wrapText`, the label font and the body painter out of `dna-orb-canvas.ts` into `sprite-paint.ts` (no Aurelia import), re-exported from the canvas module; verify the existing label-layout unit tests pass unchanged
- [ ] 2.2 Add `sprite-worker.ts` (OffscreenCanvas, results streamed 4 at a time as ImageBitmaps) and a unit test of its message contract with a stubbed `OffscreenCanvas`; verify the test passes and `npm run build` emits the worker chunk under the CSP's `worker-src 'self'`
- [ ] 2.3 Draw bubbles from sprites in `DnaOrbCanvas`: start the worker in `attached()`, request sprites for the field and the queued spawns on every field change, draw full-size bubbles directly until their sprites arrive, close bitmaps when the cache is cleared or the canvas detaches, and fall back to main-thread sprites (at most 4 new per frame) where `OffscreenCanvas` or module workers are missing or the worker errors; verify with unit tests for the direct-draw, fallback and cache-clear paths
- [ ] 2.4 Move the reveal marks to the frame that draws each name (sprite or direct), and verify unit tests covering "Revealed bubble names fade in on real time" › "Name preparation has not finished" and › "Reported name time follows the screen"; the existing "Normal frame rate", "Slow frames" and "Reduced motion" tests still pass
- [ ] 2.5 Pass a `drawLabel` callback to `AbsorptionAnimator` that pastes the tapped bubble's name sprite, with today's `fillText` as the fallback; verify a unit test that the callback is used when a sprite exists and the fallback otherwise
- [ ] 2.6 Compare screenshots of the bubble field, the reveal and an absorption between `main` and the branch with the harness from 1.1; verify the bubble pixels match (the absorbing name differs only as design D6 states)

## 3. Frontend: physics and tap (design D3, D4, D5, D7)

- [ ] 3.1 Enable Matter.js sleeping and wake every body on add, remove, fade-out start, queued spawn and wall rebuild; verify unit tests covering "Physics-Based Bubble Animation" › "Bubbles at rest stay where they are" and › "Field change wakes the bubbles at rest"
- [ ] 3.2 Queue tap-origin spawns (3 per frame) and set `collisionFilter.mask = 0` on fading bodies (restored on revive); verify unit tests that a 30-artist top-up enters over 10 updates and that a fading body no longer collides, and that the existing bubble-physics tests pass
- [ ] 3.3 Cache the canvas size in `sizeCanvas()` and drop the per-frame `getBoundingClientRect()` from `render()`; verify the existing canvas tests pass, and the harness shows no `getBoundingClientRect` in the loop's profile
- [ ] 3.4 Add `IAudioEngine.prepare()` (context and noise buffer, still resumed only by `unlock()` in a gesture) and call it within 1 s of attach; verify unit tests that `prepare()` creates a suspended context without resuming it, and that "Sound Respects Mute and Volume Settings" tests still pass

## 4. Frontend: decorative animations (design D8)

- [ ] 4.1 Rebuild the swap tile's three sparkles as HTML elements over the SVG animated by `transform` and `opacity` with the same timing and reduced-motion rule; verify the `discovery-swap-button` stories pass with updated visual baselines (pinned container) and a trace of the idle field shows no per-frame layout from the tile
- [ ] 4.2 Move the onboarding progress sheen to a pseudo-element moved by `transform: translateX`; verify the `onboarding-progress` stories pass with updated visual baselines and the idle trace shows no per-frame paint from the row

## 5. Frontend: frame-timing event (design D9)

- [ ] 5.1 Add `perf.discovery_frames` to `analytics-events.ts` and record frame samples in the canvas loop, sending once per visit on detach or first hide when at least 30 samples exist; verify unit tests covering "Discovery frame timings are reported" › "Fan leaves Discovery after browsing bubbles", › "Paused time is left out", › "Visit too short to measure", › "One event per visit" and › "Analytics off"

## 6. Frontend: start-up (design D10, frontend #782)

- [ ] 6.1 Take signed-in and guest cold-load traces of `/discovery` and `/dashboard` on the spec's cold-load reference setup (Slow 4G, 4x CPU, 375 px, repeat visit), list every main-thread item over 50 ms before the first route paints, and record the list with a remove-or-defer decision per item in design.md D10
- [ ] 6.2 Remove or defer each item decided in 6.1 (one commit per item, leaving items owned by `meet-timetable-render-budget` to it); verify per item with a before/after trace recorded in design.md D10 and with the existing unit and E2E tests of the touched components
- [ ] 6.3 Re-measure "Cold load meets a time budget" (about 10 loads each, signed-in and guest) and record `ghosts_ms` and `first_name_ms` medians in design.md; verify both medians are within the 6.0 s and 3.0 s bounds

## 7. Frontend: integration check

- [ ] 7.1 Run the harness from 1.1 on the branch build on the frame reference setup (about 5 runs), record the numbers in design.md, and verify the bounds of "Physics-Based Bubble Animation" › "Idle field of 50 bubbles" and › "Tap on a bubble in a field of 50"
- [ ] 7.2 Run Discovery in a local production build with Playwright (guest: cold load, tap three bubbles, search and follow, switch to All Nearby and back, reduced motion on), and verify no console error and the existing Discovery E2E tests pass

## 8. Production check after release

- [ ] 8.1 After the release is deployed, read the `perf.discovery_frames` and `perf.discovery_reveal` events in PostHog for the testers' devices (read-only), and record the medians per browser in design.md next to the long-animation-frame figures in proposal.md
