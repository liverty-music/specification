## Why

The sibling change `defer-dashboard-reentry-render` found the dashboard's laser
beam positioning itself from JavaScript that measured every matched card on
every frame. That one loop accounted for `Forced reflow while executing
JavaScript took 58194ms` in a production trace, and it also silently defeated the
viewport-scoped rendering the same change was introducing. Replacing it with a
CSS scroll-driven animation deleted the scroll listener, the animation-frame loop
and the measurement — about 130 lines — and removed the cost entirely.

That was not an isolated mistake. A sweep of the frontend found the same shape in
five more places: work the platform will do declaratively, carried instead by
hand-written JavaScript.

The sweep also claimed two surfaces kept an animation frame loop running while
nothing could see it. **That claim was wrong, and checking it is what this change
now does about suspension.** The frontend has exactly two continuous loops — the
discovery orb and the welcome page's ambient glow — and both already suspend on
every condition that can occur to them, including the case where two conditions
overlap. Neither can be scrolled out of view: the glow is a viewport-fixed
full-screen canvas, and the orb sits in a non-scrolling viewport-height layout.

What is actually missing there is not the behaviour but any statement of it. The
suspension lives in two routes' event handlers, nothing tests it, and a third
surface added tomorrow would have no contract to meet and no test to fail. It is
also the kind of correctness that fails silently: a surface that never suspends
looks completely normal.

The pattern is worth addressing as one change because the judgement is the same
each time — ask what the platform already provides, and check the current
behaviour before assuming it is absent.

## What Changes

**Write down the suspension contract that already holds, and test it**

- The discovery orb (`dna-orb-canvas.ts`) exposes `pause()`/`resume()`, and
  `discovery-route.ts` calls them on entering and leaving search mode (where the
  orb's container is `display: none`) and on `visibilitychange`. It also handles
  the overlap: returning from a background tab resumes only if search mode is not
  still active. `resume()` resets the frame timebase, and the loop caps its delta.
- The welcome page's ambient glow (`ambient-glow.ts`) suspends on
  `visibilitychange`, and under reduced motion never registers the listener at
  all, so a resume cannot start a loop the fan opted out of.
- One gap remains, and it is the kind this capability exists to close.
  `onVisibilityChange` resumes only if search mode is not active, but
  `onExitSearchMode` resumes unconditionally — leaving search mode in a hidden tab
  would wake the orb. It is unreachable today only because every exit path is
  user-initiated and so needs the tab in the foreground: correct by a property of
  the callers rather than of the suspension. One guard closes it.
- Otherwise no behaviour changes. The change adds the `offscreen-work-suspension`
  capability describing this contract, and the tests that hold both surfaces to
  it — including the properties that are currently correct by accident rather than
  by design: both overlap orderings and the timebase reset.
- The audit that established this is part of the change: the conditions a surface
  can actually be in are a property of its layout, and assuming "scrolled out of
  view" without checking is exactly the error this section corrects.

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
- Changing how either continuous surface suspends. Section 1 established that
  both are already correct; this change writes the contract down and tests it.

## Capabilities

### New Capabilities

- `offscreen-work-suspension`: the app-wide contract that continuous work —
  animation frame loops, physics simulation, canvas painting — runs only while
  the surface it draws is actually being rendered, and resumes in time to be
  seen, without advancing, without waking against a reduced-motion preference,
  and without one suspension condition cancelling another. Today each surface
  decides all of this for itself and both get it right; nothing records the
  contract and nothing would catch a third surface getting it wrong.

### Modified Capabilities

Two are contingent, and neither delta exists yet.

`onboarding-celebration` admits exactly one no-animation case today (reduced
motion). Adopting `@starting-style` adds a second — a browser below its Baseline
toggles instantly — so if the celebration item proceeds, that capability needs a
delta saying so.

`bottom-sheet-ce`'s stated behaviour does include
component-managed focus trap, background `inert` and Escape, so moving those to a
modal dialog would change it — but that depends on the spike's outcome, and this
change does not commit to a requirement it has not yet established. If the spike
says the dismiss gesture and a modal dialog can coexist, the delta is added then.

## Impact

- **Frontend only**, across unrelated surfaces: `celebration-overlay.ts` (+ its
  CSS), `coach-mark.ts`, `press-feedback.ts` (+ its CSS), and — only if the spike
  allows — `bottom-sheet.ts` (+ its CSS and spec). `dna-orb-canvas.ts` and
  `ambient-glow.ts` gain tests, plus a single guard on the orb's search-mode exit.
- **No visual change is intended anywhere.** Each item either removes work the
  fan cannot see or swaps the mechanism behind an unchanged appearance, so the
  component tests and visual baselines are the check that nothing moved.
- **Risk is concentrated in the bottom sheet**, which is the single dialog
  primitive for every overlay in the app; a regression there is app-wide. That is
  why it is gated behind a spike and sequenced last.
- **The suspension half is now test-only**, so its risk is that a test encodes
  today's implementation rather than the contract, and blocks a legitimate future
  refactor. The requirements are written in terms of conditions and outcomes, not
  of `pause()`, `visibilitychange` or search mode, and the tests should follow.
- Browser-support and current-behaviour claims are checked rather than inferred.
  The sibling change twice shipped assumptions that measurement disproved, and the
  original form of this change asserted a defect in code that did not have one.
