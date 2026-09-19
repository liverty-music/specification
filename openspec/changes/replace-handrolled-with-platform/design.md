## Context

See proposal.md. This change generalises a result from
`defer-dashboard-reentry-render`: the dashboard's laser beam was positioned by
JavaScript that measured every matched card each frame, which produced
`Forced reflow while executing JavaScript took 58194ms` in a production trace and
also defeated that change's viewport-scoped rendering. Replacing it with a CSS
scroll-driven animation removed the loop, the listener and the measurement.

That change also taught how to decide these questions. Three assumptions written
into its design — that relocating work to `attached()` would produce an earlier
paint, that returning any promise from `attaching()` would yield one, and that a
time-based reveal could serve scrolled-to content — were all disproved by
measurement, and one CSS bug (a time value where a scroll-driven animation
requires `auto`) failed silently with no error anywhere. Platform-support and
platform-behaviour claims here are therefore taken from the project's platform
guidance, and anything the guidance does not cover is verified before it is
relied on rather than reasoned about.

Platform facts this design rests on:

- **`@starting-style` and `transition-behavior: allow-discrete`** are Baseline
  since 2024-08-06 (Chrome 117, Firefox 129, Safari 17.5). Where unsupported,
  elements toggle instantly instead of animating.
- **`<dialog>` shown with `showModal()`** natively provides a focus trap, a
  backdrop and Escape dismissal, and `closedby="any"` adds light-dismiss without
  script. Critically, **`showModal()` and the `popover` attribute are mutually
  exclusive programmatic states** — an element cannot be both at once.

## Goals / Non-Goals

**Goals:**

- The rule that no surface performs per-frame work while the browser is not
  rendering it is written down and tested, rather than upheld by coincidence in
  two routes.
- Behaviour the platform already provides is not re-implemented in the component.
- No visual change anywhere.

**Non-Goals:**

- Rewriting how the discovery orb renders; only when it runs.
- The laser beam, already converted by the sibling change.
- Replacing `IntersectionObserver` where it drives application logic rather than
  gating rendering work.

## Decisions

- **Decision: Establish the current behaviour before specifying a fix — which
  here removed the fix.** The sweep that started this change asserted that the orb
  and the glow keep running while nothing can see them. Reading the code and the
  layout disproved both halves:
  - Neither surface can be **scrolled out of view**. The glow canvas is
    `position: fixed; inset: 0` — a viewport-fixed full-screen element. The orb
    sits in `.discovery-layout`, which is `block-size: 100%; overflow: hidden`
    inside a `100dvh` app shell, so the route does not scroll at all.
  - The orb **already suspends** on both conditions that can occur to it. It
    exposes `pause()`/`resume()`, and the route calls them on entering and leaving
    search mode — where its container is `display: none` — and on
    `visibilitychange`.
  - The glow **already suspends** on `visibilitychange`, the only condition that
    can occur to it.

  So the mechanism this design originally chose does not apply. A
  `contentvisibilityautostatechange` handler would never fire on either surface:
  one is always in the viewport, and `display: none` does not produce that event.
  This is recorded rather than deleted, because the reasoning was sound and only
  its premise was false — the conditions a surface can be in are a property of its
  layout, and have to be read rather than assumed.

- **Decision: Specify the contract and test it, rather than change behaviour.**
  Two of the properties the surfaces satisfy are the kind that hold today and
  break quietly tomorrow, and neither is written down or covered by a test:
  - **Overlapping conditions.** Returning from a background tab resumes the orb
    only `if (!this.search.isSearchMode)`. Each condition read alone looks
    correct; the bug appears only when both apply and lifting one wakes a surface
    the other still requires to stay stopped.
  - **The timebase.** `resume()` sets `lastTime = performance.now()`, and the loop
    caps its delta at 32ms. Without either, a resume after a long pause feeds the
    simulation an enormous interval and it explodes rather than continues.

  The requirements are written in terms of conditions and outcomes, not in terms
  of `pause()`, `visibilitychange` or search mode, so a future refactor of how
  suspension is wired does not have to rewrite the spec.

- **Decision: Reduced motion is part of the suspension contract, not separate from
  it.** The glow paints a single static frame under `prefers-reduced-motion` and
  never registers its `visibilitychange` listener, so no resume can start a loop
  the fan opted out of. That is the correct shape and it is easy to lose in a
  refactor that centralises suspension, so it becomes a requirement.

- **Decision: Suspension preserves the last frame.** Pausing must not clear the
  canvas: a surface that is partially visible, or that becomes visible a frame
  before work resumes, has to keep showing what it last drew. This is what makes
  the suspension invisible, and it is the difference between pausing a loop and
  tearing down a renderer. Both surfaces already do this; the requirement records
  it so a renderer teardown is never mistaken for a pause.

- **Decision: Replace the celebration overlay's `transitionend` choreography with
  declarative entry/exit.** The component currently listens for `transitionend`
  and carries a flag for whether a fade-out is in progress, purely to know when
  to call back. `@starting-style` plus discrete-transition behaviour expresses the
  same thing in the stylesheet, so both the listener and the flag go. Its
  dismissal callback still needs to fire at the end of the exit; whether that
  reads a transition event or is restructured is an implementation detail, but
  the flag tracking "am I fading" should not survive.

- **Decision: Gate the bottom sheet behind a spike, and sequence it last.** The
  sheet is the single dialog primitive behind every overlay in the app, so a
  regression is app-wide. Its capability currently specifies component-managed
  focus trap, background `inert` and Escape, and its dismiss gesture is built on
  scroll-snap with the popover state as the mechanism. Because `showModal()` and
  `popover` cannot both apply, adopting a modal dialog means giving up the
  current dismiss architecture, not layering onto it. The spike settles whether
  the gesture can be rebuilt on a modal dialog — `closedby="any"` covers
  light-dismiss, but the scroll-snap drag is the open part. Only if it can does
  this change touch the sheet, and only then does `bottom-sheet-ce` get a delta.

- **Decision: Prefer a visibility query over a box measurement in the coach
  mark, but confirm it first.** The coach mark measures an element's box solely
  to test `width > 0 && height > 0`. A purpose-built visibility query expresses
  that intent without reading layout. The project's guidance does not cover that
  API, so its support and its exact semantics — particularly whether it reports
  what this check actually wants — are verified before the swap; if it does not,
  the measurement stays and the finding is recorded as a non-issue.

- **Decision: Move the ripple's sizing into CSS, keep its positioning in script.**
  The ripple measures its host on every press to compute a diameter. Container
  query units let the stylesheet size it against the host directly, and the
  pointer event already carries element-relative coordinates, so the measurement
  is unnecessary for both. This is a simplification, not a performance fix — it
  happens once per press, not per frame — and it is sequenced accordingly. The
  keyboard-activation path has no pointer coordinates and centres the ripple; that
  path must keep working.

## Risks / Trade-offs

- **The suspension half ships no behaviour change**, so its risk is the opposite
  of the usual one: a test that encodes today's wiring rather than the contract
  would block a legitimate refactor while proving nothing. The requirements avoid
  naming the mechanism, and the tests should be written against them.
- **The bottom sheet is the highest-risk item in the change** and the one whose
  outcome is unknown when the change is written. It is gated and sequenced last
  precisely so the rest can ship whatever the spike concludes.
- **Suspension is invisible when it works, which makes regressions quiet.** A
  surface that fails to resume looks like a frozen canvas, and a surface that
  never suspends looks completely normal. Both need explicit checks rather than
  relying on noticing.
- **Nothing here should change appearance**, so the component tests and committed
  visual baselines are the real safety net; a baseline diff in this change is a
  signal that something was got wrong, not something to regenerate.

## Migration Plan

Each item is independent and separately revertible. Order: the suspension audit
and its tests first (no production change, so nothing can regress), then the
celebration overlay, then the coach mark and ripple simplifications, then the
bottom-sheet spike and — only on a positive result — its rewrite.

## Verification

- Tests that hold both surfaces to the contract: work stops and resumes for each
  condition that can occur to them, an overlapping condition keeps a surface
  suspended, a resume does not advance the simulation, and a reduced-motion
  surface is never started into a loop.
- A device check that the orb resumes showing a complete frame, since a preserved
  last frame is the one property a unit test cannot see.
- Component tests and visual baselines unchanged across every item.
- For the bottom sheet, if it proceeds: focus containment, Escape, background
  inertness and the dismiss gesture all verified against the existing capability's
  scenarios before the delta is written.

## Open Questions

- Whether the bottom sheet's scroll-snap dismiss can be rebuilt on a modal dialog
  at all. This is the spike, and a negative result is an acceptable outcome that
  removes the item from the change.
- Whether the coach mark's visibility query reports what that check needs, which
  decides whether that item happens.
- Whether any surface other than these two will ever need suspension. The
  contract is written app-wide on the strength of two instances, which is thin; if
  a third never appears, the requirements are still the only record that the two
  are correct on purpose.
