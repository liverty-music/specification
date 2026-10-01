## 1. Baseline and spike (design.md D0, S1)

- [x] 1.1 Record the D0 baseline trace on the reference profile with the production account (≥200 dates): Timetable re-entry from Discovery — INP, Scripting / Rendering / Painting self-time, and time under `repeat` + `event-card` activation; also cold-load render time after data arrives. Verify by attaching the numbers to this change's design.md under D0
- [x] 1.2 Spike S1: in a Storybook story of `concert-highway` with 225 groups, insert 12 groups above a scrolled position and confirm the viewed group stays put under default scroll anchoring, with sticky date separators; record whether `overflow-anchor: none` on the separator is needed. Verify by recording the result under D1
- [x] 1.3 Spike S2: in current Chrome, confirm `view-timeline: attr(data-beam-name type(<custom-ident>)) block` on a card resolves a named `ViewTimeline` usable from the beam overlay through `timeline-scope`. Verify by recording the result under D3

## 2. Per-card cost (app-shell: "Press is acknowledged by a state layer and shape morph"; live-highway: "The beam effect is presentational and costs nothing to render")

- [x] 2.1 Add the shared pressed-state utility (state layer + corner morph on `:active`, `position: relative`, reduced-motion fallback) and remove `press-feedback` from `event-card.html`, `dashboard-route.html` and `my-artists-route.html`; delete `custom-attributes/press-feedback.ts`, its tests and registration. Verify with component tests for "Pressing a control shows the state layer and shape change" (computed `:active` style), "Reduced motion still acknowledges", and "Building a screen does no press-related work" (no listener or style read on attach)
- [x] 2.2 Add `artistHue` to the UI-only `Concert` fields, computed once where timetable concerts are built; bind it as `--artist-hue` inline in `event-card.html` and `event-detail-sheet.html`; delete the `artist-color` attribute and its registration; amend the frontend CUBE CSS convention to allow inline custom properties from data. Verify with a unit test on the mapping and the existing card/detail-sheet colour stories unchanged
- [x] 2.3 Remove `beam-index`, `data-beam-index` and `beam-timeline` from `event-card`; add a one-time, id-derived `data-beam-name` on every card, a beams-on marker on the highway host, and the beams-on CSS rule deriving `view-timeline` from it with typed `attr()` for matched cards; make `buildBeamIndexMap()` run only while `showBeams` is true and name beams by concert (D3); delete `custom-attributes/view-timeline.ts`. Verify with highway tests for "Disabled beams cost nothing" (no card declares a beam timeline, no observed beam binding, no beam set computed), "Turning beams on reaches the concerts already on screen" (toggle on in place, no group or card rebuilt) and the existing beam stories ("Only concerts on screen are lit", beams land on their cards) passing

## 3. Date window (route/dashboard: "The timetable renders a window of dates around the fan", "Timetable rendering cost is bounded…")

- [x] 3.1 Render `visibleGroups` (initial window around an `initialAnchor` bindable, 12 groups) with top and bottom sentinels grown by one `IntersectionObserver` (D1); recompute the window around the current top date when `dateGroups` is replaced; point the beam map and `scrollAnchor` getter at `visibleGroups`. Verify with highway tests for "Only the window is built" (225 groups in, ≤24 built), "Scrolling down reaches every later date", "Scrolling up from a restored date reaches earlier dates without a jump" and "Lanes stay aligned in every built group" (three-lane and two-lane)
- [x] 3.2 Remove `content-visibility` / `contain-intrinsic-size` from the date group and rewrite the Storybook regression guard that asserts them to assert the window instead. Verify the story guard and `make lint` pass

## 4. Re-entry (route/dashboard: "Re-entry restores the date the fan was looking at", "Page identity paints independent of the timetable render"; bottom-nav-bar: "Menu-tab navigation never waits on data")

- [x] 4.1 Move cached-group reflection from `attached()` to `bound()` in `dashboard-route.ts`, pass the saved anchor to the highway's `initialAnchor`, restore in the highway's `attached()`, and remove `runTasks()` from the re-entry path (D2). Verify with dashboard/highway tests for "Re-entry restores the same date, at any depth" (first render already positioned, no skeleton rendered), "The anchored date is gone" (nearest later date), "A cached result is reflected from the component lifecycle", and "Deferring the render preserves load-path side effects" (background refresh, celebration latch, deep-link)
- [x] 4.2 Confirm `scripts/verify-route-loading` still passes unchanged (nothing is assigned in `loading()`) and update its explanatory comment and the `instant-page-switch` E2E expectation that the skeleton is seen on re-entry. Verify `make lint` and the functional Playwright project pass

## Moved out of this change

- Task 2.4 (a trace after group 2 alone) is superseded. Groups 2–4 shipped in
  one release, so no production build with group 2 alone existed to trace. The
  after-traces under design.md D0 measure all of them together.
- Tasks 5.1 (meeting the 200 ms bounds on the reference profile) and 5.2
  (settling the window size from that trace) move to the follow-up change
  `meet-timetable-render-budget`. The after-traces under D0 recorded the
  bounds as not yet met: re-entry INP 602 ms, cold load ≈ 1.4 s.
