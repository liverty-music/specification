## Why

Discovery's bubble field does not stay smooth on a phone. In production (PostHog, last 30 days, few testers) iPhone Safari reports long animation frames with a median of 177 ms and a 90th percentile of 694 ms on Discovery, and the Pixel 8 Pro 132 / 146 ms. A spike on 2026-11-07/08 measured the real production build with 50 bubbles in desktop Chrome with a real GPU and 4x CPU throttling: the field idles at 29–59 frames per second, and the 2.5 s after a tap drop to 36–39 frames per second with frames of up to 317–367 ms. The causes are spread over the whole page, not one component, so they are fixed together. The start-up cost before the first route paints (frontend #782) is the other half of why a fan waits on Discovery, and the owner asked to fix it in the same change.

## What Changes

**Discovery frame rate (50 bubbles)**

- Each bubble's soft rim, gradient and name are painted once into a sprite, off the main thread (a Web Worker with `OffscreenCanvas`), and pasted every frame. Today every frame redraws a `shadowBlur` rim for every bubble. A full-size bubble whose sprite has not arrived yet is drawn directly, so a name is never delayed by the sprite.
- The physics engine lets settled bubbles sleep and wakes all of them whenever the field changes.
- The 30 bubbles a tap adds leave the tap point a few per frame instead of all on one point in one frame; bubbles fading out stop pushing the others.
- The bubble that flies into the orb draws its name from its sprite instead of laying out text at a new size every frame.
- The canvas size is read on resize only, not every frame.
- The sound engine's audio graph is built within 1 s of opening Discovery, not inside the first tap.
- The swap tile's sparkles and the onboarding progress row's sheen animate on the compositor only; today they force style, layout and paint on every frame.
- Discovery reports its frame timings once per visit, so the effect can be checked on the testers' phones after release.

**Start-up (frontend #782)**

- Trace the signed-in and guest cold loads of `/discovery` and `/dashboard`, list the main-thread work before the first route paints (template compilation, forced layout in `attached()`, `showPopover()` on attach, analytics init), and remove or defer each item the traces show to be avoidable. The existing cold-load budget stays the bound.

Not changing: what the field contains, the physics feel, the sounds, the look of a bubble, the order of the tap feedback. HTML-in-Canvas, WebGL and per-frame text drawing were measured and rejected (design.md D1).

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `components/infrastructure/fan/web/route/discovery`: "Physics-Based Bubble Animation" gains a frame-rate bound with 50 bubbles, idle and after a tap. "Revealed bubble names fade in on real time" states that a name prepared off the main thread is still drawn on time. One requirement is added: Discovery reports its frame timings once per visit.

Unchanged:
- `components/infrastructure/fan/web/global/analytics`: the new event follows its existing consent, query-string and display-mode rules; no rule there changes.
- `components/infrastructure/fan/web/global/app-shell` and `components/infrastructure/fan/web/route/dashboard`: the start-up work removes waste without changing behaviour; the dashboard's render bounds belong to the in-flight change `meet-timetable-render-budget`.

## Impact

- **Frontend only.** `src/components/dna-orb/` (canvas, physics, absorption animator, a new sprite worker and its shared paint module), `src/services/audio-engine.ts`, `src/components/discovery-swap-button/`, `src/components/onboarding-progress/`, `src/services/analytics-events.ts`, and the start-up path (`src/main.ts`, components that read layout or open popovers in `attached()`).
- **Browsers.** The worker needs `OffscreenCanvas` 2D (Safari 16.4 and later). Testers' iPhones run iOS 18.5 (PostHog, last 90 days); a browser without it draws on the main thread as today.
- **Verification.** No dev environment: unit tests, the frame and cold-load measurements on the reference setups before and after (design.md), and production frame timings from the new event.
