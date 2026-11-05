## Context

See proposal.md (Why) for the four defects and their measured causes. The constraints that shape the approach:

- The stylesheet lint bans `z-index` (`frontend/stylelint.config.js`, `property-disallowed-list`). The decision in this change's planning was to keep the ban, so no fix may depend on a stacking order.
- Overlays (sheets, snacks, the FAB) already live in the top layer, whose order is the order they were opened in and cannot be set by the page.
- `shared/ui/snack-bar/` is shared with the organizer console.
- The dev environment is stopped; every check runs in Storybook (both motion projects), unit tests or read-only production checks.

## Goals / Non-Goals

**Goals:**
- Fix each defect by removing its cause, not by layering a workaround over it.
- Make the class of defect visible in Storybook: route layouts and the snack stack get stories that fail when it returns.

**Non-Goals:**
- The timetable's sticky date separators (`concert-highway.css`) can be covered by later cards by the same mechanism. This change does not touch them; the My Artists route story pattern is what a follow-up uses to check them.
- The bottom sheet's internals (the `replace-handrolled-with-platform` spike owns them).
- The dashboard's filter sheet and its URL parameters.

## Decisions

### D1. My Artists: the table body is the only scroll container

`table` becomes a two-row grid (`auto` header, `minmax(0, 1fr)` body) with the five columns, and `thead`, `tbody` and `tr` take the columns with `grid-template-columns: subgrid`. `tbody` scrolls; `.artists-fieldset` no longer does. `thead` loses `position: sticky` and its `backdrop-filter`.

Measured in Chromium with this structure, 40 rows, positioned labels and a `view-transition-name` on every row: after `tbody.scrollTop = 300` the header has not moved, the element under a header label is that label, every header cell's left edge equals its column's cells' left edge, and the accessibility tree is `table > rowgroup > row > columnheader` / `rowheader` / `cell`.

Alternatives:
- `z-index` on the sticky `thead`, scoped by `isolation: isolate`. It is the standard way to order positioned boxes (MDN, stacking context), but the ban stays.
- Removing every positioned element and the permanent `view-transition-name` from the rows. It works today, but the next positioned element in a row brings the defect back and no lint catches it.
- A separate decorative header band outside the table. It duplicates the column headers for assistive technology.

The edit-mode bottom padding (so the last row clears the Done bar) moves from the fieldset to `tbody`. The `[data-hype-header]` coach-mark target stays on `thead`.

### D2. One snack component, with the `Snack` event as its model

`snack-bar.ts` copies eight fields of each `Snack` into a `SnackItem` record and removes the record on the popover's `toggle` event. Measured: `toggle` fires at the same millisecond as `hidePopover()`; the 500 ms exit transition ends 490 ms later. Removing the record lets Aurelia drop the element before its exit plays.

A `<snack-item>` custom element replaces both the record and the `repeat` over plain `<output>` elements. It binds the published `Snack` directly and owns only what exists while it is shown (the timer and its remaining time). Its `attached()` calls `showPopover()`; its `detaching()` calls `hidePopover()` and returns `Promise.all(host.getAnimations().map(a => a.finished))`. Aurelia's documented pattern for exit animation is exactly this: the framework keeps the DOM until a promise returned from `detaching()` settles (docs.aurelia.io, "Component Lifecycle Animations"). The motion itself stays in CSS (`@starting-style` and `allow-discrete` transitions) with the motion tokens it uses today. `<snack-bar>` keeps the list, the limit of three, `replaceKey` and the subscription; removing a `Snack` from the list starts its exit.

Alternative: keep the record and wait for `transitionend` before removing it. The snack-bar spec rules out `transitionend` (it does not fire when the transition is skipped), and the record would still duplicate `Snack`.

### D3. Snacks stack with CSS anchor positioning, oldest lowest

Each open snack carries `anchor-name: var(--_self)`, and every snack but the lowest sets `position-anchor: var(--_below)` and `inset-block-end: calc(anchor(top) + var(--space-3xs))`. The names come from data as inline custom properties (`--_self: --snack-<id>`), which the frontend's inline-style rule allows. The lowest snack keeps today's `--_inset-end` placement above the navigation bar and any banner.

The direction is fixed by the platform. Measured in Chromium: a popover opened later can anchor to one opened earlier, but a popover opened earlier cannot anchor to a later one (it falls back to the top of the viewport). So the oldest snack is the lowest, and a new snack appears above the others instead of pushing them up. When a lower snack leaves, the next one's `--_below` points to the snack before it and it moves down.

Alternatives:
- One popover for the whole stack, with the snacks as flex items. The stack must then be re-shown (hidden and shown) whenever a dialog opens after it, which replays every snack's entry motion; the spec also forbids manual re-insertion.
- Offsets computed in script from measured heights. It is the hand-rolled layout this codebase is removing elsewhere.

The coach mark already relies on CSS anchor positioning (`coach-mark.css`), so this adds no new browser requirement. A browser without it shows the snacks overlapped, as today.

### D4. Swipe to dismiss with scroll snapping

Inside each snack, a horizontal scroller holds three slots: an empty one, the snack's content, and another empty one, with `scroll-snap-type: x mandatory` and the content centred at rest. An `IntersectionObserver` on the content dismisses the snack when less than half of it is visible. This is the mechanism the bottom sheet already uses for its downward dismiss, so the browser provides momentum, snapping back and cancelation. `pointerdown` on the snack pauses its timer (the remaining time is kept); `pointerup` and `pointercancel` resume it. Under reduced motion the exit transition is already zero, so a swiped snack disappears at once.

Alternative: pointer events with a drag threshold and a velocity check. Rejected because it re-implements what scroll snapping does.

A swipe dismisses through the same path as every other dismiss, so `onDismiss` (an unfollow's undo commit) fires once.

### D5. All Nearby filter sheet and its launcher item

The `.nearby-filters` chip row is removed. A new `<nearby-filter-sheet>` (a `bottom-sheet`) holds two rows, area and period, each showing its value. A tap on a row closes the filter sheet and then opens the existing `user-home-selector` or `date-range-sheet`, so two sheets are never open at once. `DiscoveryRoute` registers `[filter, help]` while the view is `nearby` and `[help]` otherwise, re-registering on every view switch (the launcher replaces an owner's set). The filter item's `isOn` is "area override set, or period is not the `week` preset", the same contract as the dashboard's filter item.

The date label (`date-range-sheet`'s emitted `label`, localized as today) moves from the chip to the period row.

### D6. The area and the date preset are kept in device storage

A new module in `src/adapter/storage/` reads and writes `StorageKeys.nearbyFilter`:

```ts
interface StoredNearbyFilter {
  /** ISO 3166-2 code, or null to follow the fan's home area. */
  areaCode: string | null
  /** The last applied quick preset; null after a custom range. */
  datePreset: 'weekend' | 'week' | 'month' | null
}
```

`NearbyVisit` starts from it; applying a preset or an area writes it; applying a custom range writes `datePreset: null`, so the next visit starts from `week`. Choosing the fan's own home area writes `areaCode: null`. Every read and write is wrapped in `try`/`catch`, and an unreadable value starts from the defaults. The value holds only the fan's own input, which the frontend's review rule allows in storage.

### D7. Card state: hype from follows, journey from the journey store

`ConcertStore.toDateGroupsForLocation` takes the fan's `hypeByArtist` (from `FollowStore`, filled by `FollowService.List`, or from the device for a guest) and the journey map (`TicketJourneyStore`, filled by `TicketJourneyService.List`). A performer the fan follows gets their hype; any other performer gets `watch`, which `isHypeMatched` never matches. The journey map goes to `toDateGroups` as on the dashboard.

`NearbyVisit.cache` keeps the `ListByLocation` proximity groups (the RPC response) instead of converted date groups, so a change of hype or journey re-derives the cards without a request. `NearbyConcerts` watches `journeyStore.journeyMap` and `followStore.hypeByArtist` and re-derives, as `DashboardRoute.onJourneyMapChanged` and its hype watch do. A visit straight to `/discovery?view=nearby` calls `journeyStore.load()`, which returns an empty map for a guest without a request.

Values the cards show and where they come from: artist name and lane from `ConcertService.ListByLocation`; hype from `FollowService.List`; journey status from `TicketJourneyService.List`; purchased count from the purchased-ticket store, unchanged.

### D8. Storybook: every story renders, and route stories are allowed

- `.storybook/screenshot.ts` imports `vitest` at module load, and loading `vitest` outside its runner throws (`chai.use(JestChaiExpect)` reads the missing worker state). The fix moves the import inside the `MODE === 'test'` branch as `await import('vitest')`. Commit 7e9cd168 guarded only the call, so it never took effect.
- `FourStacked` additionally asserts that the boxes of the open snacks are pairwise disjoint and that the oldest is lowest.
- The frontend `AGENTS.md` story rule changes from "Do NOT story route/page components" to: a route may have stories when every store and RPC client it resolves is registered as a fake through `defineAureliaStory({ items })` and nothing reaches the network; canvas surfaces (`dna-orb`) stay excluded. Storybook's guidance on page stories (mock the data and modules a connected component depends on) supports this.
- `my-artists-route.stories.ts` renders the route with 40 fake follows, scrolls `tbody` by 300 px, asserts the hit test of each header label, and compares a screenshot baseline made in the pinned container (`visual-baselines` skill).

## Risks / Trade-offs

- [Safari and Firefox may drop table semantics when table elements change `display`] → Check with VoiceOver on iOS Safari against production after release. If the table is announced as plain text, add explicit `role="table"`, `rowgroup`, `row`, `columnheader`, `rowheader` and `cell`.
- [The new stacking order differs from today's intent (newest lowest)] → The platform allows only this order without a stacking hack; a new snack no longer moves the snack the fan is about to tap.
- [Swipe scrollers inside every snack add work to each snack] → At most three snacks plus the update snack are open at once.
- [Snack changes reach the organizer console] → Its snack stories (`console-consolesnackbar--*`) run in the same Storybook job.
- [A kept area override hides a later change of the home area] → Choosing the home area clears the override, and the filter item shows its active state while an override is set.

## Migration Plan

Frontend-only release with no data migration. The new storage key starts empty, so the first visit after release uses today's defaults. Rollback is a revert; the leftover storage key is ignored by the previous version.
