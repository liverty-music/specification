## Context

See proposal.md. Two spikes were run before this design was written, and their
measurements — not inference — decide the load-bearing choices below. Both are
reproducible; the harnesses are described under "Spike evidence".

Aurelia facts relied on (Aurelia 2.0.0-rc.2, confirmed against the official docs
and then verified by measurement):

- There are **two lifecycles**, and the design must place each concern on the one
  that owns it:
  - **Route lifecycle** (`canLoad` → `loading` → … → `loaded`, and `canUnload` →
    `unloading`) knows about navigation: params, query, where we came from, and
    whether we are leaving. The official descriptions are explicit: `loading` is
    the **pre-activation** hook ("fetch data, prepare state"), `loaded` is the
    **post-activation** hook, and `unloading` is the **pre-deactivation** hook
    ("cleanup, **save state**").
  - **Component lifecycle** (`binding` → `bound` → `attaching` → `attached` →
    `detaching` → `unbinding`) knows about the DOM: `bound` is where refs become
    available, `attached` is where the element is in the DOM.
- `attaching()` and `detaching()` **may return a Promise, which Aurelia awaits**,
  and `attached()` runs only after `attaching()`'s promise resolves. This change
  does not use that facility — entrance motion is CSS and blocks nothing — but it
  is recorded because it is what made "let the animation be the yield" look
  plausible before it was measured.
- Official guidance on async data (`components/lifecycle-diagrams.md`) ranks the
  options by what they block: `async binding()` blocks all children and is wrong;
  `async loading()` blocks the view swap; `attached()` + `void` blocks nothing.
  The repo's existing `non-blocking-menu-navigation` capability picked a fourth
  point on that spectrum — `loading()` + `void` — which starts the fetch earliest
  while blocking nothing. That choice stands.

## Spike evidence

**Spike 2 — subgrid flatten × containment** (static HTML, Chromium 1243, 390px
viewport). Four variants of the real `concert-highway` structure, measured by
`getBoundingClientRect()` rather than by eye:

| Variant | Lane left offsets | Aligned to stage header | Containment active |
| --- | --- | --- | --- |
| V0 current (subgrid ×4) | 17 / 135.66 / 254.33 | yes (baseline) | n/a |
| V1 current + `content-visibility` | lanes collapse to full width, stacked | **NO** | — |
| V2 flattened | 17 / 135.66 / 254.31 | yes (≤0.02px) | n/a |
| V3 flattened + `content-visibility` | 17 / 135.66 / 254.31 | yes (≤0.02px) | **yes** |

- V1 reproduces the reverted P2 failure exactly, confirming the diagnosis:
  containment severs a subgrid chain that crosses the contained boundary.
- V2/V3 confirm the hypothesis that **subgrid is not load-bearing here**: the
  root columns are equal fractions and there is **no grid column-gap** (the only
  `gap` in the component is the month separator's flex gap), so a group that
  declares the same `grid-template-columns` lands on identical column positions.
- Sticky date separator pinned at the same offset (9.2px) in V0, V2 and V3.
- The matched-card glow is not clipped in V3 (lane `overflow` stays `visible`).
- **Scroll-height drift**: V0/V2 `scrollHeight` 4776 vs V3 **5192** (+416px),
  because `contain-intrinsic-size`'s literal fallback (180px) differs from the
  real group height (159.2px) for groups never yet rendered.

**Spike 1 — lifecycle vs paint** (Aurelia 2.0.0-rc.2 via CDN ESM, router,
4× CPU throttle, 1500 rows). "Shell-only frames" counts rendering opportunities
where the App Shell frame was on screen while the heavy list was still empty:

| `rows` assigned in | `attaching()` returns | Shell-only frames | Shell lead |
| --- | --- | --- | --- |
| `loading()` | — | **0** | none (current behavior) |
| `attached()` | nothing | **0** | none |
| `attached()` | `Promise.resolve()` | **0** | none |
| `attached()` | `setTimeout(0)` promise | 1 | 180 ms |
| `attached()` | `element.animate(…).finished` | **5** | **277 ms** |

Conclusions, which overturn earlier assumptions in this change:

1. Moving the assignment to `attached()` is **not sufficient** — on its own it
   produced zero shell-only frames. `attached()` is inside the activation task,
   before the browser's first paint.
2. **Returning a Promise from `attaching()` is not automatically a yield.**
   `Promise.resolve()` is a microtask and produced zero frames. Only promises
   settling on a macrotask or an animation frame create a paint opportunity.

A second run then measured the render block against list size, which reframed
the whole question:

| Rows rendered | Render block | Navigation |
| --- | --- | --- |
| 1500 (≈ today's unwindowed timetable) | 177.7 ms | 219 ms |
| 400 | 76.8 ms | 112 ms |
| 120 (≈ one windowed viewport) | **44.2 ms** | 82 ms |
| 60 | 16.3 ms | 49 ms |

3. **The yield was treating a symptom.** Once containment bounds the render to
   the viewport, a single paint is fast, so no scheduling primitive is needed on
   any path — and forcing a frame-only paint on re-entry would cost a frame and
   flash an empty frame over content the fan has already seen.

**Spike 3 — `content-visibility` × CSS animation** (Chromium, same harness
style). An off-screen date group under `content-visibility: auto` had its CSS
animation **running on schedule** (`currentTime` 633 ms sampled at t=600 ms,
against 600 ms with containment off). Containment does not defer animations.
Two consequences the motion design depends on: a time-based stagger consumes
itself off screen, so it is visible only for content in view at first render;
and it has always finished before a group is scrolled into view, so the
time-based and view-timeline triggers never animate the same element at once.

**Production baseline** (own account, Chrome device emulation 412x915, **CPU
throttling off**). Captured after the spikes, and it moved the problem by an
order of magnitude:

| | Cold load | Tab-switch re-entry |
| --- | --- | --- |
| INP | — | **64,472 ms** |
| Rendering | 21,352 ms | 24,556 ms (first 31 s; recording stopped early) |
| Total captured | 31,625 ms | 31,253 ms |
| Date groups | **225** | 225 |

Two things follow. First, the figures this change was originally scoped against
(~23 groups, ~2.6 s, INP 2,536 ms) came from a smaller account and understated
the problem by roughly 25x; every decision below is now sized against 225
groups. Second, 225 groups is about seven months of concerts, because the query
is bounded below (today onward) and not above — so part of the residual is fetch
scope, not render scope, and this change can only address the latter.

The cold-load trace also reported `Forced reflow while executing JavaScript took
58194ms`, which is what surfaced the beam-loop decision below.

## Goals / Non-Goals

**Goals:**

- The timetable frame (stage header + lanes) paints at tab-switch without data.
- Off-screen date groups skip style, layout and paint.
- Date groups reveal top-to-bottom as data arrives and as they are scrolled into
  view; re-entry restores instantly at the previous scroll position with no
  entrance animation.
- Every bottom-nav tab honours the non-blocking contract.

**Non-Goals:**

- `virtual-repeat` / `@aurelia/ui-virtualization`.
- The CSS render-cost work (P1 shipped, P2 reverted) in the sibling change.
- Loading skeletons for Tickets / Order / Discovery.

## Decisions

- **Decision: Flatten the subgrid chain; the date group declares its own
  columns.** Measured in Spike 2 (V2/V3 within 0.02px of baseline). The group
  stops being a subgrid participant of the scroll container, so containment no
  longer severs a chain that crosses it; `.lane-grid` may still subgrid off the
  group because that chain is internal to the contained element. This is the
  enabling refactor — every decision below depends on it.

- **Decision: Restore viewport scoping with `content-visibility: auto` on the
  flattened group.** This is P2, re-applied on a structure that can carry it.
  Spike 2 V3 shows containment engaging (off-screen groups fall back to the
  intrinsic size while the on-screen group renders naturally) with alignment,
  sticky behavior and the matched-card glow all preserved.

- **Decision: Decouple the laser beam from card rendering entirely; drive it from
  CSS.** `updateBeamPositions()` read `getBoundingClientRect()` on every matched
  card each frame and only then decided whether that card was visible. That is
  the `Forced reflow while executing JavaScript took 58194ms` in the cold-load
  trace, and it would also force layout of every skipped group once containment
  lands — cancelling the containment win.

  Gating those reads on `contentvisibilityautostatechange` was implemented first
  and works, but it patches a coupling that should not exist: the beam is a
  decorative overlay whose only input is where its concert sits on screen. That
  is the scrollytelling pattern — a target element animated from the scrollport
  position of a different element — so it belongs in CSS:
  - each matched card declares a named `view-timeline` (the name is generated per
    beam and set inline, since the set is dynamic);
  - the scroll container carries `timeline-scope` listing those names, because the
    beams live in a viewport-fixed overlay and are not descendants of the cards;
  - each beam binds `animation-timeline` to its card's timeline over `cover`.

  Animate `transform: scaleY()`, never a registered custom property: animating one
  forces a full-subtree style recalc every frame, which is exactly the cost P1
  deleted from this component.

  Spike 4 measured the whole mechanism in Chromium: runtime-generated timeline
  names resolve (`ViewTimeline`), a fixed-overlay beam tracks its card's scroll
  position (progress 0 → 0.741 → 1, `scaleY` 1 → 0.259 → 0), and the values are
  **identical with `content-visibility: auto` applied to the groups** — containment
  and the timeline coexist.

  This deletes the scroll listener, the rAF loop, the geometry reads and the
  anchor→element map: about 47 of `concert-highway.ts`'s 242 lines, and the
  forced-reflow root cause with them.

- **Decision: Accept no beams where scroll-driven animations are unavailable.**
  Scroll-driven animations are limited availability (Chrome/Edge 115, Safari 26,
  not Firefox). The `beam-effect-toggle` capability defines the beam as a visual
  effect that is **off by default** and user-toggled, so it is decorative by its
  own specification and the platform guidance's progressive-enhancement path
  applies: feature-detect, no fallback, and explicitly no `scroll-timeline-polyfill`.
  The trade is deliberate — Firefox users lose a decorative effect that is off
  unless they turn it on, and every user stops paying a per-frame layout cost.

- **Decision: Treat `contain-intrinsic-size` drift as a scroll-restoration
  problem, not a cosmetic one.** Spike 2 measured +416px of scroll-height error
  over 30 groups. Use `contain-intrinsic-size: auto <fallback>` so each group's
  real height is remembered once rendered, and pick the fallback from the real
  median group height rather than a round number. Because a restored scroll
  offset is meaningless against a wrong scroll height, restoration must be
  applied **after** the cached groups render, and must tolerate the list being
  shorter than the saved offset (clamp, do not throw).

- **Decision: Split "start the fetch" from "reflect render state", and place
  each on the lifecycle that owns it.** This is the root-cause statement for the
  original bug: the cache fast path did *presentation* work in a *pre-activation
  route* hook, so the component's first render already contained every group.
  - Starting the fetch stays in `loading()` + `void` — navigation-scoped, earliest
    possible, blocking nothing. The existing capability is right about this.
  - Reflecting render state (including the cached fast path) moves to the
    component lifecycle, so the first render contains the frame and skeleton only.

- **Decision: Do not schedule a paint. Bound the render instead.** The earlier
  `queueAsyncTask`, and its replacement of yielding from `attaching()`, both
  treated a symptom. Spike 1 (rerun) measured the render block against list size
  at 4x CPU throttle: 1500 rows 177.7 ms, 400 rows 76.8 ms, 120 rows (about one
  windowed viewport) **44.2 ms**, 60 rows 16.3 ms. Once containment bounds the
  work to the viewport, a single paint is fast, and forcing an earlier
  frame-only paint would cost an extra frame and flash an empty frame over
  content the fan has already seen. `attaching()` therefore returns nothing and
  no scheduling primitive is used anywhere. If a yield were ever needed, the
  standards primitive is `scheduler.yield()`, not `setTimeout(0)` -- but the
  simpler answer is to not need one.

- **Decision: Cold load needs no yield either.** With no cached data there is
  nothing to render but the frame and skeleton, and the fetch's own await is the
  natural yield. This is already how the cold path behaves today, which is why it
  never froze; only the cache fast path did.

- **Decision: Keep render-state reflection off the pre-activation hook, for
  contract reasons, not paint reasons.** The broadened
  `non-blocking-menu-navigation` forbids synchronous render-state assignment in
  `loading()`. The relocation stands on that rule. It does **not** by itself
  produce an earlier paint -- Spike 1 measured zero frame-only paints from the
  relocation alone.

- **Decision: Entrance motion is CSS on the date group, with two triggers that
  cannot collide.** The motion unit is the date group, so one keyframe set serves
  both cases:
  - *Initial reveal* uses a time-based stagger via `sibling-index()`
    (Baseline newly available, 2026-08-18; Chrome 138, Firefox 154, Safari 26.2).
    A `--sibling-index` custom-property fallback declaration precedes it for
    browsers below that Baseline, set by a short guarded script.
  - *Scroll reveal* uses a view timeline (`animation-timeline: view()` with
    `animation-range: entry`), feature-detected with
    `@supports ((animation-timeline: view()) and (animation-range: entry))` --
    the `animation-range` term is required to exclude partial implementations.
    Scroll-driven animations are limited availability (Chrome 115, Safari 26, not
    Firefox); the effect is decorative, so this is progressive enhancement with
    no fallback and explicitly **no** `scroll-timeline-polyfill`.
  Spike 3 measured that `content-visibility: auto` does **not** defer animations
  in skipped subtrees (an off-screen group's animation ran on schedule:
  `currentTime` 633 ms at t=600 ms, against 600 ms with containment off). The
  time-based stagger therefore consumes itself off screen and is visible only for
  content in view at first render -- exactly the intended behavior -- and it has
  always finished before a group is scrolled into view, so the two triggers never
  animate the same element at once and need no gating.

- **Decision: Re-entry restores in one cheap paint.** Entrance motion is
  suppressed on the cached path. With the view timeline this is partly
  structural: a group already in view sits past its `entry` range and renders in
  its final state without animating. Re-entry correctness is a render-cost
  property, bounded by containment, not a paint-ordering property.

- **Decision: The App Shell frame is gated on "settled and empty", not on
  `dateGroups.length`.** The stage header and lane columns render whenever the
  view is loading or populated, and are withheld only for a settled-empty result.
  Both empty-state placeholders — the guest one and the "no concerts" one — must
  be gated on a settled condition, never inferred from `length === 0 &&
  !isLoading`, which cannot distinguish "not assigned yet" from "genuinely zero".

- **Decision: Do not overload `isLoading`.** It also guards
  `refreshInBackground()`. The skeleton and the empty-state gate read a distinct
  settled flag so the background refresh still fires on re-entry.

- **Decision: Save scroll at `unloading`, restore at `attached()` after data.**
  `unloading` is officially the "save state" hook and is navigation-scoped, which
  matches a per-route scroll memory. Restoration needs the DOM and the rendered
  list, so it belongs to the component lifecycle and must be sequenced after the
  cached groups are in place.

- **Decision: Broaden the non-blocking contract rather than re-deriving it.**
  `non-blocking-menu-navigation` already states the rule correctly; it names only
  the three tabs that existed when it was written. Widen it to every bottom-nav
  tab and add that a synchronous render-state assignment in `loading()` blocks
  first paint exactly as an `await` does. Fix Settings accordingly.

## Risks / Trade-offs

- **The flatten changes lane alignment in a way the spike did not model** (real
  cards have container queries, variable counts and the `hideAway` two-column
  mode) → Mitigation: assert lane/stage-header column geometry in a component
  test at both three-lane and `hideAway` widths, not only visually.
- **`contain-intrinsic-size` drift corrupts a restored scroll offset** →
  Mitigation: restore after render, clamp to `scrollHeight`, and verify on device
  that returning to a deep scroll position lands within a card of where it left.
- **Re-entry has no yield by design** → Mitigation: the device trace must show
  re-entry INP within budget; if not, add a non-microtask yield on the cached
  path (measured at 180 ms lead with `setTimeout(0)`).
- **Storybook regression guard currently asserts the opposite of this change** —
  it requires NO `content-visibility` and that the `<li>` keeps its subgrid. It
  encodes the P2 revert and must be rewritten with the flatten, not deleted.
- **`verify:build-templates` marker drift** — the dashboard template changes; a
  removed marker class breaks the production image build, not CI.
- **Entrance animation on cold load competes with the first data render** → the
  animation is on the frame, not the cards, so it must not delay the list beyond
  its own duration; keep it short and honour `prefers-reduced-motion` (which must
  then fall back to a non-microtask yield, since no animation means no yield).

## Migration Plan

Ships in the normal frontend release. The flatten and the containment land
together — containment without the flatten is the reverted P2 bug. Rollback is a
revert of the CSS plus the template gate.

## Verification

Verification happens on production. The dev environment is stopped, so there is
no pre-production place to measure this — and the 225-group volume that makes
the change necessary exists on a real account regardless. Promotion is a release
publish that retags the digest `main` already built, so the measured build is
byte-identical to the merged one.

On the reference profile (Pixel 8 or emulation + 4× CPU), signed in with a
populated timetable:

1. Cold load: the stage header and lane columns paint while the fetch is in
   flight; date groups reveal top-to-bottom as the data arrives; no empty-state
   flash.
2. Re-entry from another tab: the restored timetable paints in a single frame
   whose render block is bounded by the viewport, with the header/nav and the
   timetable arriving together and INP substantially below the pre-change
   baseline. No entrance animation, restored at the previous scroll position.
3. Scrolling reveals subsequent dates, animated where supported, without a
   scrollbar jump.
4. Background refresh still swaps fresh data; the celebration fires once when
   due; a `/concerts/:id` deep-link still opens the detail sheet.
5. Settings: tapping the tab swaps the view immediately; the previous screen is
   never held while its RPCs resolve.

## Open Questions

- The `contain-intrinsic-size` fallback value — derive from the real median group
  height on the reference dataset during implementation.
- Whether `prefers-reduced-motion` cold load should use `setTimeout(0)` as its
  yield or accept a single coalesced paint; decide against the measured render
  cost once containment is in.
