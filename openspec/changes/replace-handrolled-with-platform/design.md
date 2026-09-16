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

- **`content-visibility` and `contentvisibilityautostatechange`** are Baseline
  since 2025-09-15 (Chrome 108, Firefox 130, Safari 26). Where unsupported the
  property is ignored and the event never fires, so the work simply continues as
  it does today — a progressive enhancement with no fallback required.
- The guidance distinguishes the two ways to ask "can this be seen":
  `contentvisibilityautostatechange` for **rendering-heavy work**, because it is
  tied to the browser's own rendering lifecycle and fires within the pre-render
  margin; `IntersectionObserver` for **application logic** tied to exact visual
  visibility. The event does not bubble reliably, so it is listened for on the
  element itself or with `{ capture: true }`.
- **`@starting-style` and `transition-behavior: allow-discrete`** are Baseline
  since 2024-08-06 (Chrome 117, Firefox 129, Safari 17.5). Where unsupported,
  elements toggle instantly instead of animating.
- **`<dialog>` shown with `showModal()`** natively provides a focus trap, a
  backdrop and Escape dismissal, and `closedby="any"` adds light-dismiss without
  script. Critically, **`showModal()` and the `popover` attribute are mutually
  exclusive programmatic states** — an element cannot be both at once.

## Goals / Non-Goals

**Goals:**

- No surface performs per-frame work while the browser is not rendering it.
- Behaviour the platform already provides is not re-implemented in the component.
- No visual change anywhere.

**Non-Goals:**

- Rewriting how the discovery orb renders; only when it runs.
- The laser beam, already converted by the sibling change.
- Replacing `IntersectionObserver` where it drives application logic rather than
  gating rendering work.

## Decisions

- **Decision: Suspend continuous work from `contentvisibilityautostatechange`,
  not from an `IntersectionObserver`.** Both the orb and the ambient glow are
  rendering-heavy, which is the case the event exists for; it also fires inside
  the pre-render margin, so a surface is resumed slightly before it is on screen
  and never shows a stale or half-drawn first frame. Using an
  `IntersectionObserver` instead would answer a subtly different question and
  resume later. The host surface takes `content-visibility: auto` so the browser
  has a reason to skip it in the first place.

- **Decision: Keep the existing `visibilitychange` handling as well, rather than
  replacing it.** The ambient glow already pauses on a background tab. The two
  conditions are different — a hidden tab and an off-screen element — and the
  event only covers the second. Both remain.

- **Decision: Suspension preserves the last frame.** Pausing must not clear the
  canvas: a surface that is partially visible, or that becomes visible a frame
  before work resumes, has to keep showing what it last drew. This is what makes
  the suspension invisible, and it is the difference between pausing a loop and
  tearing down a renderer.

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

- **The orb resumes where it paused, not where it would have been.** A physics
  simulation that stops for ten seconds and restarts has not advanced. Whether
  that reads as natural or as a stutter is a judgement that needs a device check,
  not a test.
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

Each item is independent and separately revertible. Order: the two suspension
items first (highest value, contained blast radius), then the celebration overlay,
then the coach mark and ripple simplifications, then the bottom-sheet spike and —
only on a positive result — its rewrite.

## Verification

- Device checks that the orb and the glow stop when scrolled away and when the
  tab is backgrounded, and that both resume showing a complete frame.
- A check that a suspended surface keeps its last frame rather than blanking.
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
- Whether the orb should resume on the pre-render margin or wait until it is
  genuinely on screen, if the margin turns out to start the simulation noticeably
  early on a long page.
