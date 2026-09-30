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

**Baseline (2026-09-29, production, before this change).** DevTools trace
`Trace-20260929T170418.json.gz`, soft navigation Discovery → Timetable on the
production account.
- Conditions: iPhone SE emulation, 4× CPU throttling. The person who
  recorded it set 4×, but that trace's metadata does not record the setting.
  Two browser extensions were active (≈ 40 ms in total).
- Tap: INP **265 ms** (pointerdown 53 ms; click to next paint 265 ms). That
  paint is the shell's header and nav only.
- About 1.0 s after the tap, a single task of **5,438 ms** runs: one
  `RunMicrotasks`, which is the dashboard's activation. No frame is produced
  during it. The Frames track shows a single 12.2 s frame, and soft-navigation
  LCP is **6.78 s**. CLS is 0.
- Inside that task:
  - **487 forced style recalculations (2,197 ms) and 487 forced layouts
    (1,864 ms), 4,061 ms in total, or 75% of the task.** All 974 have the same
    top frame: the `press-feedback` custom attribute's `attached()`
    (`main-50IWXAAP.js:1450:19476`). It sets `data-press-feedback` and then
    reads `getComputedStyle(el).position` for each of the 487 tappable
    elements, as Aurelia activates them.
  - The remaining ≈ 1.3 s is building and binding every date group and card
    (the `repeat` / `event-card` activation), plus GC.
- Main thread over the whole recording (183 ms – 13.57 s): Rendering
  5,144 ms, Scripting 3,369 ms, System 957 ms, Painting 181 ms.

**Baseline, cold load (2026-09-29, production, before this change).** Trace
`Trace-20260929T171652.json.gz`, a reload of `/dashboard` on the production
account.
- Conditions: **4× CPU throttling** (recorded in the trace metadata), iPhone
  SE emulation. Two extensions were still active.
- `ListByFollower` finished at 99,427 ms. A single task (`TimerFire`) then ran
  for **9,100 ms**, and the next frame came 160 ms after it ended. From data
  arrival to the timetable's first frame: **≈ 9.4 s** (the spec bound is
  ≤ 200 ms).
- Inside that task: **486 forced style recalculations (3,937 ms) and 486
  forced layouts (2,943 ms), 6,879 ms or 76%**. All of them come from
  `press-feedback`'s `attached()` (`main-50IWXAAP.js:1450:19476`); the rest
  is building every date group and card.
- The re-entry above and this cold load together are the D0 baseline on the
  reference profile (4× CPU). The after-traces (5.1) must be taken the same
  way, preferably without extensions.

**Baseline caveat.** v1.72.9 (released 2026-09-30 01:35 UTC, between these
baselines and this change) already removed `press-feedback`'s computed-style
read (frontend#675). The after-traces below therefore measure that fix and
this change together.

**After-trace, cold load (v1.72.11, 2026-09-30).** Trace
`Trace-20260930T124842.json.gz`, a reload of `/dashboard`, 4× CPU.
- From `ListByFollower` finishing to the first frame showing concerts:
  **≈ 1.4 s** (baseline ≈ 9.4 s).
- No forced reflow from `press-feedback` remains.
- The spec bound (≤ 200 ms) is **not met**. What remains:
  - 340 ms converting the response for all loaded dates
    (`protoGroupToDateGroup` alone is 113 ms);
  - 198 ms rendering the window;
  - 344 ms for the first layout and paint;
  - 182 ms for the next paint.
- The trace also showed the loading placeholder and the first concerts in the
  same frame, then the concerts jumping up. See the fixes below.

**After-trace, tab-switch re-entry (v1.72.11, 2026-09-30).** Trace
`Trace-20260930T170512.json.gz`, Discovery → Timetable, 4× CPU.
- INP **602 ms** (baseline 265 ms). The timetable now renders inside the tap's
  task, as D2 intends; the baseline painted only the shell and then froze for
  5.4 s.
- Tap to the timetable on screen: ≈ 0.6 s (baseline > 6.5 s).
- The spec bound (INP ≤ 200 ms) is **not met**. The 511 ms task breaks down
  into:
  - ≈ 100 ms of forced layout for the restore's `scrollIntoView`;
  - 55 ms of template creation (`innerHTML`) per navigation;
  - ≈ 80 ms of `showPopover` plus another forced style recalculation, both
    from an `attached()`;
  - ≈ 280 ms rendering the window.

**Fixes after release.**
- **frontend#679 (v1.72.11).** The deep-link path's `runTasks()` (see D2)
  exceeded Aurelia's 100 ms synchronous budget on slow devices. It threw
  "Potential deadlock" and dropped every queued task, the render included.
  This was reproduced at 10× CPU on the release before this change as well.
  The sheet now opens in a task queued behind the filter's URL write.
- **frontend#680 (v1.72.12).** The window's groups were inserted when the
  window was sliced, while the placeholder's `if` read a getter that
  re-evaluated a task later. One frame painted both, which caused CLS 0.56 on
  a cold load (0.60 before this change) and, from #679 on, on a deep-link too.
  `showSkeleton` is now a field set in the same step as the window.
  Production v1.72.12 records CLS 0 on both.

@spec-manual components/infrastructure/fan/web/route/dashboard "Tab-switch re-entry does not freeze on rendering" -- the D0 after-trace (task 5.1) on the reference profile with the production account (≥200 dates): Timetable re-entry from Discovery, INP ≤ 200 ms. Its second clause, the timetable in the same next paint with no skeleton between, is also asserted frame by frame by the functional E2E for "Header and nav switch before the timetable renders".

@spec-manual components/infrastructure/fan/web/route/dashboard "First dashboard load render cost is reduced" -- the D0 after-trace (task 5.1): main-thread time to render the timetable once its data arrives on a cold load, ≤ 200 ms on the reference profile. A number measured on a throttled reference device, which the CI browsers cannot stand in for.

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
- Prepend stability: the highway keeps the fan's place itself. Before a change
  that adds dates above the fan (top growth, or `dateGroups` replaced while
  attached), it reads the date at the top edge and the offset into it (the
  `scrollAnchor` getter). It then applies the change and puts that date back
  (the setter: `scrollIntoView` on the group, plus the offset). Aurelia's
  keyed `repeat` finishes the window's DOM synchronously when `visibleGroups`
  is assigned: cards, text and final heights are there before the method
  returns. So no flush and no scheduling is needed. Reading the position after
  the change lays out the new groups before the next frame would have. That is
  the same layout work done earlier, not extra work, and it happens once per
  growth step during a scroll, never on a tap. The scroll container sets
  `overflow-anchor: none`, so browser scroll anchoring never corrects the same
  change a second time.

**Spike S1 result (2026-09-28).** Browser scroll anchoring was tried first and
rejected for this list. Setup: Chromium 153, E2E on the guest dashboard with
225 dates, re-entry deep in the list, scrolling up 150px per step.
- Groups of uniform height: every prepend was anchored (18 of 18).
- Groups of uneven height (1–3 cards per date): about 40% of prepends were
  corrected by a fixed +285px instead of the 1740–1790px added, so the view
  jumped by 1400–1900px. The same steps failed on every run.
- Setting `overflow-anchor: none` on the sticky separators, on the edge
  markers, or on the cards, lanes, lane grids or month separators changed
  nothing. So did making the separators static. The root cause was not found.
- A prepend at scroll offset 0 is never anchored.
- Safari does not implement scroll anchoring, as far as is known, so the CSS
  route would jump there on every prepend.
With the highway keeping its place, every step of the same E2E stays within
2px ("Scrolling up from a restored date reaches earlier dates without a
jump").
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
re-entry path (`reflectCachedGroups`) is removed. The deep-link one was removed
after release (frontend#679, see D0): it deadlocked on slow devices. The
mode-switch View Transition callback keeps its `runTasks()`, because it must
capture the new DOM synchronously. It is not on the tab-switch path and is left
to a separate change.

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
  attribute. **Every** card carries a fixed timeline name as data,
  `data-beam-name="--beam-<concertId>"`, bound one-time. One-time is safe
  because the lane `repeat` is keyed by `ev.id`, so a view never changes
  concert, and the name depends on the id alone. Whether the concert is
  matched stays on the live `data-matched`, so a background refresh that
  changes the match is still reflected. A stylesheet rule that applies only
  while the highway host carries its beams-on marker declares the view
  timeline:
  `concert-highway[data-beams] .event-card[data-matched][data-beam-name] {
  view-timeline: attr(data-beam-name type(<custom-ident>)) block }`. The
  overlay and `timeline-scope` use the same names. No script touches a card.
- Turning beams on or off only flips the host marker and builds or clears the
  beam set, a cost proportional to the number of beams. No date group or card
  is rebuilt, and cards added as the window grows arrive already named. This
  is what the fab-menu "Enabling the beam effect" scenario needs: the toggle
  is on the dashboard, so the beams must appear without leaving the page.
- The `beam-timeline` custom attribute is deleted.

**Browsers without typed `attr()`** (Safari as of 27.0; it ships in Safari
Technology Preview and is an Interop 2026 focus area): the declaration is
invalid and ignored, no timeline exists, and the beams stay at their
`scaleY(0)` base — i.e. absent — which is the degradation the spec already
requires, with the toggle and everything else unchanged. There is no browser
or OS detection, no `@supports` branch and no Safari-specific switch: the same
stylesheet starts drawing beams in a browser the day it ships typed `attr()`,
with no code change.

**Spike S2 result (2026-09-28).** Chromium 153 (Playwright headless shell,
standalone page): a card carrying `data-beam-name="--beam-c-1"` under a rule
`#host[data-beams] .card[data-beam-name] { view-timeline:
attr(data-beam-name type(<custom-ident>)) block }` computes
`view-timeline-name: --beam-c-1`, and a beam in a sibling overlay with
`animation-timeline: --beam-c-1`, scoped by `timeline-scope` on the common
ancestor, gets a `ViewTimeline` and follows it (scaleY 0.5 at the midpoint of
its range). Removing the host's beams-on attribute leaves the card with
`view-timeline-name: none` and the beam with no timeline, so scoping the rule
to "beams on" works. No Safari device is available to the team, so there is
no check on Safari hardware. By CSS error handling, a browser that does not
parse typed `attr()` drops the declaration at parse time with no script
error. The functional E2E `beam-degradation` reproduces that browser in
Chromium by deleting exactly that one rule. It then checks, with the effect
on, that no card declares a timeline and no beam is lit, that the toggle is
still offered and still persists `liverty:beams:enabled`, and that the
timetable builds the same groups and opens the detail sheet as with the
effect off.


- *Alternative — the highway queries the matched cards and sets
  `view-timeline` on them*: works in Safari, but keeps a DOM query and style
  writes into child elements for an opt-in effect. It would also have to redo
  those writes on every window growth, data refresh and keyed view reuse.
  Rejected in favour of the CSS-only form once Safari support was ruled out of
  scope.
- *Alternative — name only matched cards, one-time, and rebuild on toggle*
  (add `showBeams` to the group `repeat` key): the name then cannot reach
  cards that are already built without a rebuild. The window only grows during
  a visit, so the rebuild has no upper bound after deep scrolling, and the key
  hides a dependency. Rejected.
- *Alternative — a live `data-beam-name.bind` per card*: toggling works, but
  every card keeps an observer while beams are off, which is the default.
  Rejected.
- *Future — CSS `ident()`*: `ident("--beam-" attr(data-concert-id))` would let
  a card carry only a generic concert id. It is not supported in Chromium 153
  (checked 2026-09-28: `CSS.supports` false, no timeline created). Revisit
  once it ships.

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

- [Browser scroll anchoring is unreliable on this list and absent in Safari]
  → Measured in S1. The highway keeps its place itself (D1) and the scroll
  container opts out of browser anchoring.
- [`keepingPlace` relies on the keyed `repeat` updating the DOM synchronously
  when `visibleGroups` is assigned] → Verified in S1 on Aurelia 2.0.0-rc.2 and
  covered by the scroll-up E2E, which fails at the first jump if a framework
  upgrade makes the update asynchronous.
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
