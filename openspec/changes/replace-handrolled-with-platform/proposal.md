## Why

The sibling change `defer-dashboard-reentry-render` found the dashboard's laser
beam positioning itself from JavaScript that measured every matched card on
every frame. That one loop accounted for `Forced reflow while executing
JavaScript took 58194ms` in a production trace, and it also silently defeated the
viewport-scoped rendering the same change was introducing. Replacing it with a
CSS scroll-driven animation deleted the scroll listener, the animation-frame loop
and the measurement — about 130 lines — and removed the cost entirely.

That was not an isolated mistake. A sweep of the frontend found the same shape in
five more places: work the platform will do declaratively, or work that should
not be running at all, carried instead by hand-written JavaScript. Two of them
keep a continuous animation frame loop running while nothing is on screen to see
it — including the app's heaviest surface, the physics-simulated discovery orb.

The pattern is worth addressing as one change because the fix is the same
judgement each time — ask what the platform already provides — and because the
guidance for each is already documented rather than a matter of taste.

## What Changes

**Stop continuous work that nothing can see**

- The discovery orb (`dna-orb-canvas.ts`) runs a Matter.js physics simulation and
  canvas render loop whose only stop condition is the route being torn down. It
  keeps running at full rate while scrolled out of view and while the tab is in
  the background. Discovery is a route fans stay on, so this is not a brief
  window.
- The welcome page's ambient glow (`ambient-glow.ts`) already pauses when the tab
  is hidden but not when it scrolls off screen — the same fix completes it.
- Both suspend and resume from the browser's own rendering lifecycle, which is
  the documented mechanism for rendering-heavy work and distinct from asking
  whether an element is visually in view.

**Let the platform own what it already owns**

- The celebration overlay drives its entry and exit through a `transitionend`
  listener plus a state flag tracking whether a fade is in progress. Declarative
  entry/exit styling replaces both.
- The bottom sheet walks the DOM from the sheet up to `<body>`, marking every
  sibling at every level `inert`, and manages its own focus trap and Escape
  handling. A modal dialog provides all three natively. **This one is contingent:**
  the sheet's dismiss gesture is built on scroll-snap and the popover state, and
  modal dialogs and popovers are mutually exclusive programmatic states, so
  whether the two can be reconciled must be settled by a spike before anything is
  rewritten.
- The coach mark measures an element's box purely to decide whether it is
  visible, when a purpose-built visibility query exists that does not read layout.
- The press ripple measures its host on every press to size itself, when CSS can
  size it relative to the host and the pointer event already carries the
  element-relative coordinates.

Out of scope:

- Anything already using a platform primitive correctly: the coach mark's CSS
  anchor positioning, the dashboard's view transitions, and the two
  `IntersectionObserver` uses that drive application logic (starting the welcome
  demo, committing the sheet dismiss) rather than gating rendering work.
- The laser beam itself, which the sibling change has already converted.
- Rewriting the discovery orb's rendering; only its suspension is in scope.

## Capabilities

### New Capabilities

- `offscreen-work-suspension`: the app-wide contract that continuous work —
  animation frame loops, physics simulation, canvas painting — runs only while
  the surface it draws is actually being rendered, and resumes in time to be
  seen. Today each surface decides this for itself, and two decide it wrongly.

### Modified Capabilities

None declared up front. `bottom-sheet-ce`'s stated behaviour does include
component-managed focus trap, background `inert` and Escape, so moving those to a
modal dialog would change it — but that depends on the spike's outcome, and this
change does not commit to a requirement it has not yet established. If the spike
says the dismiss gesture and a modal dialog can coexist, the delta is added then.

## Impact

- **Frontend only**, across unrelated surfaces: `dna-orb-canvas.ts`,
  `ambient-glow.ts`, `celebration-overlay.ts` (+ its CSS), `coach-mark.ts`,
  `press-feedback.ts` (+ its CSS), and — only if the spike allows —
  `bottom-sheet.ts` (+ its CSS and spec).
- **No visual change is intended anywhere.** Each item either removes work the
  fan cannot see or swaps the mechanism behind an unchanged appearance, so the
  component tests and visual baselines are the check that nothing moved.
- **Risk is concentrated in the bottom sheet**, which is the single dialog
  primitive for every overlay in the app; a regression there is app-wide. That is
  why it is gated behind a spike and sequenced last.
- **The orb's suspension changes observable timing**: a paused simulation resumes
  where it left off rather than having advanced. Whether that reads as correct or
  as a stutter needs checking on device.
- Browser-support decisions follow the project's platform guidance rather than
  inference — the sibling change twice shipped assumptions that measurement
  disproved.
