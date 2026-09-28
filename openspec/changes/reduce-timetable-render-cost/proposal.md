## Why

Switching to the Timetable tab still holds the whole screen — header, bottom
nav and timetable — until the timetable has rendered, and the three appear
together. `defer-dashboard-reentry-render` accepted that ("header/nav and the
timetable arriving together") on the premise that viewport-scoped rendering
bounds the render to what is visible. It does not. `content-visibility: auto`
skips style, layout and paint for off-screen groups, but the framework still
creates and binds every date group and every concert card: on the reference
account, 225 date groups and all their cards, each card carrying three custom
attributes and a dozen bindings. That scripting cost grows with the number of
loaded concerts, not with the viewport. The spike figure the decision rested on
(44 ms for one viewport) measured a list that only had one viewport of rows in
the DOM, which is not what shipped.

The fix is to not build what is not shown, and to make each card cheap to
build, using platform CSS and plain framework templating — no scheduling
primitive, no forced flush, no virtualization plugin.

## What Changes

- **Measure first.** A device trace of the tab-switch re-entry on the
  reference account records how the interaction's main-thread time splits
  between scripting and rendering, and per-card cost, before and after.
- **The timetable renders a window of dates, not all of them.** It renders the
  dates around where the fan is — from the top on first visit, from the
  remembered date on re-entry — and adds more as the fan scrolls toward either
  edge. Dates outside the window are not built at all. This replaces
  `content-visibility` / `contain-intrinsic-size` viewport scoping, which is
  removed.
- **Re-entry renders the cached timetable directly, bounded by the window**,
  instead of first rendering the skeleton and then flushing the full timetable
  from `attached()` with a forced synchronous flush. With the render bounded
  there is nothing to defer: the first paint after the tap shows header, nav and
  the timetable at the remembered date. The forced flush (`runTasks()`) leaves
  application code.
- **Each card is cheaper to build.**
  - The contact-point ripple primitive is removed app-wide. Press
    acknowledgement is a state layer and shape change on `:active`, in CSS. The
    ripple attribute read computed style for every card on attach.
  - The beam effect costs nothing while it is off (the default). Cards carry no
    beam-specific binding or attribute; when the fan turns beams on, only the
    handful of matched cards on screen are wired to a beam.
  - A card's artist colour is computed once per concert when the timetable
    data is built and handed to CSS as a custom property, instead of by a
    per-card attribute.
- **Spec corrections.** The dashboard requirements that mandate viewport
  scoping and the "arrive together" budget are replaced; the stale per-frame
  beam-tracking requirement (the beams have been CSS-driven since
  `defer-dashboard-reentry-render`) is removed.

Out of scope:

- Changing what the timetable fetches. The window is applied to the list the
  dashboard already holds; `ListByFollower` and its `from` bound are unchanged.
- `@aurelia/ui-virtualization`. Rejected in design.md — its recycling, lack of
  grouping and lack of a scroll-to-item API collide with the beams and the
  date-anchored restore, and the window achieves the bound without it.
- Page identity (header title, active tab). That is
  `adopt-router-navigation-model`.

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `components/infrastructure/fan/web/route/dashboard`: the timetable renders a
  window of dates that follows the fan instead of scoping all dates to the
  viewport; re-entry renders the cached timetable at the remembered date in its
  first paint; the tap-to-paint budget is a number independent of how many
  dates are loaded.
- `components/infrastructure/fan/web/global/bottom-nav-bar`: a menu-tab route
  may render cached content in its first render when that render is bounded;
  the rule against assigning render state in `loading()` is kept.
- `components/infrastructure/fan/web/global/live-highway`: the beam effect costs
  nothing when disabled; the stale per-frame tracking requirement is removed.
- `components/infrastructure/fan/web/global/app-shell`: press acknowledgement
  is a state layer and shape morph; the contact-point ripple is removed.

## Impact

- **Frontend only.** `concert-highway` (window, sentinels, beams wiring,
  removal of containment CSS), `event-card` (template slimmed), the
  `press-feedback`, `artist-color` and `beam-timeline` custom attributes
  (deleted), their three template call sites, the concert-to-`LiveEvent`
  mapping (artist hue), `dashboard-route.ts` (reflection moves to the component
  lifecycle before first render; `runTasks()` calls removed), shared press CSS.
- **Tests**: the Storybook/regression guard that asserts `content-visibility`
  on date groups is rewritten to assert the window; scroll-restore tests move to
  the window; press-feedback unit tests are deleted.
- **Supersedes decisions** recorded in the archived
  `defer-dashboard-reentry-render` design ("Do not schedule a paint. Bound the
  render instead" stands; "containment bounds the render" does not).
- **Overlaps `progressive-route-rendering`**, which is still a proposal and
  requires a paint yield before expensive renders and viewport-scoped lists.
  That proposal must be revised after this change lands; it is not edited here.
- **Verification** is a before/after device trace on the reference profile.
