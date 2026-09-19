## 1. Audit — establish what is actually true before changing anything

- [x] 1.1 DONE. Enumerated every continuous animation-frame loop in the frontend: there are exactly two, `dna-orb-canvas.ts` and the `ambient-glow` custom attribute. (`dashboard-route.ts` uses a one-shot `requestAnimationFrame`, not a loop.)
- [x] 1.2 DONE. Established which "nothing can see it" conditions can actually occur to each, by reading its layout rather than assuming:
  - **The glow cannot be scrolled out of view.** `welcome-route.css` gives it `position: fixed; inset: 0; inline-size: 100%; block-size: 100%` — a viewport-fixed full-screen canvas. The welcome page's two-screen scroll-snap moves the content past it, not it past the viewport. Its only condition is a background tab.
  - **The orb cannot be scrolled out of view either.** `.discovery-layout` is `block-size: 100%; overflow: hidden` inside an app shell that is `block-size: 100dvh`, so the route does not scroll. Its conditions are search mode (`.discovery-layout[data-search-mode="true"] .bubble-area { display: none }`) and a background tab.
- [x] 1.3 DONE. Established that both already suspend correctly on every condition found in 1.2, which **withdraws the defect this change was opened on**:
  - `DnaOrbCanvas` exposes `pause()`/`resume()`. `discovery-route.ts` calls them from `onEnterSearchMode`/`onExitSearchMode` and from `onVisibilityChange`, and handles the overlap — returning from a background tab resumes only `if (!this.search.isSearchMode)`.
  - `resume()` sets `lastTime = performance.now()`, and the loop caps its delta at 32ms ("prevent physics explosions on tab-switch/GC pauses").
  - `ambient-glow` suspends on `visibilitychange`, releases both listeners in `detaching()`, and under `prefers-reduced-motion` paints one static frame and never registers the visibility listener at all — so no resume can start a loop the fan opted out of.

## 2. The orb — hold it to the contract, do not change it

- [ ] 2.1 No production change. The suspension is already correct; this section adds the tests that would catch it becoming incorrect, because today nothing would.
- [ ] 2.2 Test that entering search mode suspends the loop and leaving it resumes.
- [ ] 2.3 Test that a background tab suspends the loop and returning resumes.
- [ ] 2.4 Test the **overlapping condition**: backgrounding the tab while search mode is active, then returning to the foreground, must leave the orb suspended — search mode still applies. This is the property that reads as correct in each handler separately and is wrong only in combination, and it is currently protected by nothing.
- [ ] 2.5 Test that resuming **does not advance the simulation**: a resume after a long suspension must re-base the frame clock rather than feed the loop the elapsed interval. Assert the contract (the first frame after a resume gets a normal-sized delta), not the mechanism.
- [ ] 2.6 Test that teardown stops everything and leaves nothing scheduled.
- [ ] 2.7 Write these against the requirement wording — conditions and outcomes — not against `pause()`, `visibilitychange` or search mode by name, so a future refactor of the wiring does not have to rewrite them.

## 3. The ambient glow — hold it to the contract, do not change it

- [ ] 3.1 No production change, for the same reason. Do **not** add `content-visibility` here: the canvas is viewport-fixed, so it can never be skipped and `contentvisibilityautostatechange` would never fire.
- [ ] 3.2 Test that a background tab suspends the loop and returning resumes it.
- [ ] 3.3 Test the reduced-motion path: under `prefers-reduced-motion` the attribute paints once and starts no loop, and no visibility transition starts one either.
- [ ] 3.4 Test that `detaching()` stops the loop and removes both listeners.

## 4. Declarative entry and exit for the celebration overlay

- [ ] 4.1 Replace the `transitionend` listener and the fade-in-progress flag with `@starting-style` and discrete-transition behaviour. Both are Baseline since 2024-08-06, so no fallback is required; where unsupported the overlay toggles instantly instead of animating, which is acceptable for a celebration.
- [ ] 4.2 Keep the dismissal callback firing at the end of the exit. Restructure how that is detected if needed, but the flag tracking "am I currently fading" should not survive — it exists only because the choreography is in script.
- [ ] 4.3 Confirm the two celebration tiers (guest light acknowledgement, post-signup confetti) and the hand-off to the post-signup dialog are unchanged, including the one-shot storage flags.

## 5. Coach mark: visibility query instead of box measurement

- [ ] 5.1 First verify that a visibility query reports what this check actually needs — it exists to reject targets inside closed popovers that measure 0×0. The project's platform guidance does not cover this API, so confirm its support and semantics before relying on it. If it does not answer the same question, keep the measurement, record the finding as a non-issue, and skip 5.2.
- [ ] 5.2 Swap the box measurement for the visibility query. This is a layout read on a path that also retries on a timer, so removing it takes a forced layout out of a polling loop.

## 6. Ripple: size in CSS, position from the event

- [ ] 6.1 Size the ripple from CSS using container query units against its host, removing the host measurement. The diameter must still cover the host from the contact point, which is what the current calculation guarantees.
- [ ] 6.2 Take the contact point from the pointer event's element-relative coordinates instead of subtracting the host's box.
- [ ] 6.3 Keep the keyboard-activation path working: Enter/Space carry no pointer coordinates and must still ripple from the host's centre.
- [ ] 6.4 Keep the right-to-left mirroring correct — the ripple's horizontal origin is measured from the inline-start edge, which is the right edge under RTL.

## 7. Bottom sheet — spike first, rewrite only on a positive result

- [ ] 7.1 SPIKE: determine whether the sheet's dismiss gesture can be rebuilt on a modal dialog. `showModal()` and the `popover` attribute are mutually exclusive programmatic states, so this is a replacement of the current architecture, not an addition to it. `closedby="any"` covers light-dismiss; the open question is the scroll-snap drag and the `IntersectionObserver` that commits the close. Build it in isolation rather than reasoning about it.
- [ ] 7.2 If the spike is negative: stop here, record why in design.md, and leave the sheet alone. This is an acceptable outcome — the hand-rolled `inert` walk and focus trap stay, with a note explaining that they compensate for a deliberate architectural choice rather than being an oversight.
- [ ] 7.3 If the spike is positive: replace the ancestor-walking `inert` application, the focus trap and the Escape handling with what `<dialog>.showModal()` provides natively, and write the `bottom-sheet-ce` delta — its stated behaviour names all three as component-managed, so the requirement changes.
- [ ] 7.4 If it proceeds, verify against the existing capability's scenarios before considering it done: focus containment, Escape, background inertness, the dismiss gesture, reversing the gesture mid-drag, and the background remaining interactive during the close.

## 8. Tests and verification

- [ ] 8.1 SUPERSEDED by the per-surface tests in 2.2-2.7 and 3.2-3.4.
- [ ] 8.2 `make lint` + `make test`, plus the Storybook component tests.
- [ ] 8.3 Visual baselines must be unchanged across every item in this change. A baseline diff here means something was got wrong — do NOT regenerate baselines to make it pass.
- [ ] 8.4 Device check: the orb resumes showing a complete frame rather than a blank or torn canvas. This is the one property in the capability that a unit test cannot observe, so it is the only device check the suspension half needs — the rest are assertions, not judgements.

## 9. Close-out

- [ ] 9.1 Sync the `offscreen-work-suspension` delta into the main specs before archiving, plus the `bottom-sheet-ce` delta if 7.3 happened.
- [ ] 9.2 Record in the PR which items shipped and which were dropped, and for anything dropped, why — particularly the bottom sheet, whose outcome is unknown when this change is written, and the suspension fix, which was withdrawn by the audit in section 1.
- [ ] 9.3 If task 4.1 proceeds, `onboarding-celebration` needs a MODIFIED delta: it currently admits exactly one no-animation case (reduced motion), and `@starting-style` adds a second (a browser below its Baseline). That spec file does not exist under this change yet — create it with `/opsx:continue` before implementing section 4.
