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
- `attaching()` and `detaching()` **may return a Promise, which Aurelia awaits**;
  the docs present this as the mechanism for enter/leave animations, and state
  that `attached()` runs only after `attaching()`'s promise resolves.
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

Three conclusions follow, and they overturn earlier assumptions in this change:

1. Moving the assignment to `attached()` is **necessary but not sufficient** —
   on its own it produced zero shell-only frames. `attached()` is inside the
   activation task, before the browser's first paint.
2. **Returning a Promise from `attaching()` is not automatically a yield.**
   `Promise.resolve()` is a microtask and produced zero frames. Only promises
   that settle on a macrotask or an animation frame create a paint opportunity.
3. `element.animate(…).finished` — the officially documented animation
   mechanism — **is** a real yield, and the best performing one measured.

## Goals / Non-Goals

**Goals:**

- The timetable frame (stage header + lanes) paints at tab-switch without data.
- Off-screen date groups skip style, layout and paint.
- Cold load animates cards in; re-entry restores instantly at the previous
  scroll position with no entrance animation.
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

- **Decision: Take the paint yield from `attaching()`, and let the entrance
  animation be that yield.** Spike 1 shows the assignment alone changes nothing,
  and that the yield must not be a microtask. On cold load, `attaching()` returns
  the entrance animation's `finished` promise: the frame paints, the animation
  plays, then `attached()` fills in the data — one mechanism serving both the
  motion requirement and the paint requirement. This replaces the
  `queueAsyncTask` approach previously recorded in this change, which reached
  around the framework to manufacture the same yield.

- **Decision: Re-entry has no animation, therefore no yield — so re-entry
  correctness depends on the render being cheap.** The agreed behavior is
  instant restore, so `attaching()` returns nothing on the cached path and Spike
  1 predicts zero shell-only frames. That is acceptable **only because**
  containment makes the restored render small: with off-screen groups skipped,
  the work in a single paint is bounded by the viewport, not by ~23 groups. This
  couples the two halves of the change — if the flatten or the containment does
  not land, re-entry regresses to a single late paint and a minimal
  non-microtask yield must be added as a fallback.

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

## Verification (device-only — headless passkey auth is infeasible)

On the reference profile (Pixel 8 or emulation + 4× CPU), signed in with a
populated timetable:

1. Cold load: the stage header and lane columns paint before any card; cards
   animate in; no empty-state flash.
2. Re-entry from another tab: header/nav and the timetable frame paint ahead of
   the timetable render block; the cached timetable appears without an entrance
   animation, at the previous scroll position; INP substantially below the
   pre-change baseline.
3. Scrolling reveals subsequent dates without a scrollbar jump.
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
