## Context

See proposal.md — Why. Current code, in `frontend/`:

- `components/live-highway/concert-highway.html` repeats **every** date group
  (`repeat.for="group of dateGroups; key.bind: group.dateKey"`) and, inside each
  lane, every `event-card`. `concert-highway.css` puts
  `content-visibility: auto; contain-intrinsic-size: auto 192px` on each group.
- `event-card.html` carries three custom attributes per card —
  `press-feedback`, `artist-color`, `beam-timeline` — plus two `if` controllers,
  an i18n value converter and about ten bindings, several through computed
  getters.
  - `press-feedback.attached()` calls `getComputedStyle(el).position` per card
    (a forced style recalc on every card during attach), adds two listeners and
    one reduced-motion subscription.
  - `beam-timeline` exists on every card although beams are off by default;
    `beam-index.bind="beamIndexMap[ev.id] ?? null"` is evaluated for every card.
  - `concert-highway.buildBeamIndexMap()` runs on every `dateGroups` change
    regardless of `showBeams`.
- `dashboard-route.ts`: `loading()` parks cached groups; `attached()` assigns
  them, then calls `runTasks()` to force Aurelia's queued DOM writes
  synchronously, then restores the scroll anchor with `scrollIntoView`. All of
  it runs inside the activation task, so the first paint after the tap waits
  for all of it.
- `concert-store.timetableScrollAnchor` holds `{ dateKey, offset }`.

Framework facts, verified in Aurelia 2.0.0-rc.2 source:

- A controller's children (including `repeat` views) are activated
  synchronously during its activation, before its `attached()`; so in a
  component's `attached()` its repeated content is in the DOM.
- A promise returned from `attaching()` does not delay children and is not a
  paint opportunity. No framework primitive inserts a paint between the shell
  update and the routed view's render.
- `runTasks()` is documented for tests and debugging.
- The router has no keep-alive; a tab switch disposes and recreates the route.

## Goals / Non-Goals

**Goals:**

- Re-entry and first render cost bounded by a fixed window, independent of the
  number of loaded dates.
- Per-card build cost reduced by removing work that is not needed to show a
  card.
- No scheduling primitive, no forced flush, no plugin.

**Non-Goals:**

- Changing the fetch (`ListByFollower`, `from`), caching or background refresh.
- Removing dates from the DOM once built while the fan stays on the page
  (the window only grows during a visit; see D1).
- The detail sheet, All Nearby data flow, filters — unchanged beyond sharing the
  windowed highway.

## Decisions

### D0. Measure before and after, on the same account and profile

A Performance trace of Timetable tab re-entry (from Discovery) on the reference
profile (Pixel 8, or desktop with 4× CPU throttle), on the production account
with ≥200 dates. Record: INP, Scripting vs Rendering vs Painting self-time for
the interaction, and the time spent under the `repeat`/`event-card` activation.
Taken before any code change and after each of D1–D4, so each decision's effect
is separately attributable.

### D1. A date window in `concert-highway`, grown by sentinels

The highway renders `visibleGroups`, a slice `[start, end)` of `dateGroups`,
instead of `dateGroups`.

- Initial window: `start` = index of the anchor date (0 when none), minus 2 for
  context; `end` = `start + 12`. Twelve median-height groups (192 px) is about
  three phone screens. Upper bound built at first paint: 12 (the spec allows 24,
  leaving room to tune after D0).
- Growth: an empty sentinel element at each end of the list, observed by one
  `IntersectionObserver` rooted at the scroll container with a `rootMargin` of
  one screen. When the bottom sentinel intersects, `end += 12`; when the top one
  does, `start -= 12`. Clamped to the list.
- Prepend stability: the browser's CSS scroll anchoring (`overflow-anchor:
  auto`, the default) keeps the viewed content in place when content is
  inserted above it. The date separator stays out of anchor selection only if
  it is `position: sticky`; verify in the spike (S1), and set
  `overflow-anchor: none` on sticky separators if the browser picks them.
- The window only grows during a visit. Re-entry recreates the route and starts
  a fresh window at the anchor, which is the case the budget is about. Deep
  scrolling within one visit builds groups 12 at a time, each growth being a
  bounded task.
- Filters and background refresh replace `dateGroups`; the window is recomputed
  around the current top date so the fan's position survives.
- The beam and scroll-anchor APIs read `visibleGroups`, not `dateGroups`.

`content-visibility` and `contain-intrinsic-size` are removed from the date
group. With the window bounding what exists, they add a sizing estimate that
made pixel-based restore drift, and nothing else.

- *Alternative — `@aurelia/ui-virtualization` `virtual-repeat`*: official and
  compatible with rc.2, but it recycles views (per-card lifecycle is not
  reliable), has no group headers or nested virtualization, and no
  scroll-to-item API — so the date-anchored restore and the beams' per-card
  view timelines would both have to be rebuilt around it. The window gets the
  same bound without those collisions. Rejected.
- *Alternative — fetch a date range and page from the server*: changes the API
  contract and caching for a render problem. Rejected; the data is already on
  the client.
- *Alternative — keep containment and add a paint yield (`scheduler.yield`,
  rAF)*: rejected in discussion as a non-framework workaround; it also still
  builds every card.

### D2. Re-entry reflects cached groups in `bound()`, restores in the highway

`dashboard-route` reflects parked cached groups (and sets `hasSettled` /
`timetableLoaded`) in `bound()`, a component-lifecycle hook that runs after the
router's `loading()` and before the component's first render. The highway
receives the anchor as a bindable (`initialAnchor`), builds its first window
around it, and in its own `attached()` — where its repeated groups are already
in the DOM — calls `scrollIntoView` on the anchored group and applies the
remembered offset. Nothing is forced to flush, so the `runTasks()` in the
re-entry path (`reflectCachedGroups`) is removed. The two other `runTasks()`
call sites in the dashboard (deep-link filter before opening the sheet, and the
mode-switch View Transition callback, which must capture new DOM synchronously)
are not on the tab-switch path and are left to a separate change.

This is allowed by the modified bottom-nav-bar requirement: `loading()` still
assigns nothing; the reflection is in the component lifecycle and its render is
bounded by the window.

- *Alternative — keep reflecting in `attached()`*: the content is then rendered
  after the highway's `attached()`, so restoring needs a forced flush or an
  awaited settle, and the fan's first paint is a skeleton. Rejected.

### D3. Beams: named in CSS from the card's data; computed only when on

- `buildBeamIndexMap()` runs only while `showBeams` is true, over
  `visibleGroups`, and names each beam after its concert
  (`--beam-<concertId>`) instead of a running index.
- Cards lose `beam-index`, `data-beam-index` and the `beam-timeline` custom
  attribute. A matched card carries its timeline name as data
  (`data-beam-name`, bound one-time from the concert). A stylesheet rule, scoped
  to the highway only while beams are on, declares the view timeline from it:
  `view-timeline: attr(data-beam-name type(<custom-ident>)) block`. The overlay
  and `timeline-scope` use the same names. No script touches a card.
- The `beam-timeline` custom attribute is deleted.

**Browsers without typed `attr()`** (Safari as of 27.0; it ships in Safari
Technology Preview and is an Interop 2026 focus area): the declaration is
invalid and ignored, no timeline exists, and the beams stay at their
`scaleY(0)` base — i.e. absent — which is the degradation the spec already
requires, with the toggle and everything else unchanged. There is no browser
or OS detection, no `@supports` branch and no Safari-specific switch: the same
stylesheet starts drawing beams in a browser the day it ships typed `attr()`,
with no code change.

- *Alternative — the highway queries the matched cards and sets
  `view-timeline` on them*: works in Safari, but keeps a DOM query and style
  writes into child elements for an opt-in effect. Rejected in favour of the
  CSS-only form once Safari support was ruled out of scope.

### D4. Press acknowledgement in CSS; artist hue in data

- `press-feedback` is deleted and removed from its three call sites
  (`event-card`, `dashboard-route.html`, `my-artists-route.html`). A shared
  utility rule gives tappable controls a state layer (`::after` with the M3
  pressed opacity) and the corner morph on `:active`, with `position: relative`
  in the stylesheet. `event-card` keeps its `scale(0.97)` and gains the state
  layer. Reduced motion keeps the state layer and drops the transition.
- `artistHue(artistName)` is computed once per concert when `Concert` values
  are built for the timetable (new UI-only field `artistHue: number`), and the
  card passes it to CSS as `style="--artist-hue: ${event.artistHue}"`. The
  `artist-color` attribute is deleted; the detail sheet uses the same field.
  The frontend convention "templates do not carry `style`" is amended in the
  frontend's CUBE CSS notes to: a template may set CSS custom properties from
  data, and nothing else, inline.

### D5. One-time bindings are not applied to cards

Rejected for now. Background refresh replaces `dateGroups` with new objects
under the same `dateKey`, and the keyed `repeat` reuses the view — so one-time
bindings in a reused view would keep showing the old concert. D0's
after-trace decides whether observer cost is still material once D1–D4 land;
if it is, the key becomes `dateKey` plus a data version so reuse only happens
for identical data.

## Risks / Trade-offs

- [Scroll anchoring picks the sticky date separator and prepends jump] →
  Spike S1 before building D1; `overflow-anchor: none` on the separator.
- [A fan who scrolls through all 225 dates in one visit ends with every group
  built, without containment] → Accepted: each growth is 12 groups, off the
  tap interaction. If D0's after-trace shows scroll jank at depth, reinstate
  `content-visibility` on built groups (it no longer affects restore, since the
  anchor is always built).
- [No beams until a browser ships typed `attr()` (Safari as of 27.0)] →
  Accepted: the stylesheet degrades on its own and lights up when support
  lands; nothing is written per browser (D3).
- [Typed `attr()` with `<custom-ident>` behaves differently than expected in
  Chromium] → Spike S2 before building D3; fallback is the rejected
  highway-query alternative.
- [`bound()` reflection makes the first render include up to 12 groups] → That
  is the point; D0 verifies INP ≤ 200 ms. If not, reduce the initial window
  before anything else.
- [Removing the ripple is visible app-wide] → Agreed product decision; the
  state layer is the M3 Expressive press signal.

## Migration Plan

Single frontend release. No persisted-state change: `timetableScrollAnchor`
keeps its `{ dateKey, offset }` shape. Rollback is a revert.

## Open Questions

- Final window size and growth step — start at 12/12, tune from D0 within the
  spec's bound of 24.
