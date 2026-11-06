## Context

See proposal.md (Why) for the four defects and their measured causes. The constraints that shape the approach:

- The stylesheet lint bans `z-index` (`frontend/stylelint.config.js`, `property-disallowed-list`). The decision in this change's planning was to keep the ban, so no fix may depend on a stacking order.
- Overlays (sheets, snacks, the FAB) already live in the top layer, whose order is the order they were opened in and cannot be set by the page.
- `shared/ui/snack-bar/` is shared with the organizer console.
- The dev environment is stopped; every check runs in Storybook (both motion projects), unit tests, or manual checks against production after release with the developer's own fan account, which restore any follow, hype or journey they change.

## Goals / Non-Goals

**Goals:**
- Fix each defect by removing its cause, not by layering a workaround over it.
- Make the class of defect visible in Storybook: route layouts and the snack queue get stories that fail when it returns.

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

The edit-mode bottom padding (so the last row clears the Done bar) moves from the fieldset to `tbody`. The `[data-hype-header]` coach-mark target stays on `thead` (it was missing from the template, so it is added).

Found while implementing: the scroll container alone does not cover "Header stays clear while a row animates out". A row's view-transition snapshot is drawn above the page and is not clipped by `tbody`'s scroll box, so during an unfollow the rows scrolled under the header were drawn over it (measured: the header's pixels differ while the transition is held at its first frame). `tbody` therefore gets its own `view-transition-name`, every row `view-transition-group: nearest`, and `::view-transition-group-children(artist-rows) { overflow: clip }` (CSS View Transitions 2 nested groups, Chrome 140+); with it the header's pixels are unchanged during the transition. Browsers without nested groups fall back to today's flat groups.

Also found: axe in the new route story fails on two existing defects, the hype radios without an accessible name and the empty edit-mode column header. Each radio gets its tier label (Watch, Home, Nearby, Away) as a visually hidden name, and the column header a visually hidden `myArtists.table.removeCol` text.

### D2. One snack component, with the `Snack` event as its model

`snack-bar.ts` copies eight fields of each `Snack` into a `SnackItem` record and removes the record on the popover's `toggle` event. Measured: `toggle` fires at the same millisecond as `hidePopover()`; the 500 ms exit transition ends 490 ms later. Removing the record lets Aurelia drop the element before its exit plays.

A `<snack-item>` custom element replaces both the record and the `repeat` over plain `<output>` elements. It binds the published `Snack` directly and owns only what exists while it is shown (the timer and its remaining time). Its `attached()` calls `showPopover()`. A dismiss marks the `Snack` as leaving; the item then calls `hidePopover()`, waits for `Promise.all(host.getAnimations().map(a => a.finished))`, and dispatches `snack-exited`, on which `<snack-bar>` removes the `Snack` from its list. The next queued snack (D3) therefore appears only after the exit motion has ended. The motion itself stays in CSS (`@starting-style` and `allow-discrete` transitions) with the motion tokens it uses today. `<snack-bar>` keeps the queue (D3), `replaceKey` and the subscription.

Alternatives:
- Remove the `Snack` from the list at once and return the `finished` promise from `detaching()`. Aurelia keeps the DOM until that promise settles (docs.aurelia.io, "Component Lifecycle Animations"), but `<snack-bar>` would not know when the exit has ended, and would show the next snack on top of the one still fading out.
- Keep the record and wait for `transitionend`. The snack-bar spec rules out `transitionend` (it does not fire when the transition is skipped), and the record would still duplicate `Snack`.

### D3. One snack at a time, as Material 3 says

The Material 3 snackbar guidelines (m3.material.io/components/snackbar/guidelines, read 2026-11-05) say "Only one snackbar may be displayed at a time", "Consecutive snackbars must appear one at a time" and "Don't stack snackbars on top of one another", and allow that "a snackbar with updated information can immediately replace an outdated snackbar". So the fan app's `<snack-bar>` holds one visible `Snack` and a FIFO queue instead of a stack of three. When the visible snack's item dispatches `snack-exited` (D2), the next queued `Snack` is shown. A `replaceKey` match dismisses the visible snack and puts the new one at the head of the queue, or replaces a queued one in place. `handle.dismiss()` on a snack that is still queued removes it from the queue and calls its `onDismiss` once; it never gets an item.

The update snack (duration `Infinity`) gives way through a second handshake. When another snack is published while the update snack is visible, `<snack-bar>` sets the update `Snack` aside in a parked slot (not the queue) and asks its item to yield; the item hides its popover, waits for the exit animations' `finished` promise like a dismiss, and dispatches `snack-exited`; `<snack-bar>` then removes the item and shows the head of the queue, without calling `onDismiss`. When nothing is visible and the queue is empty, the parked update snack is shown again with a new item. So two snacks are never visible, and the update is neither applied nor lost; a swipe or the update action is what dismisses it.

Snacks with an action keep the 10-second display time instead of M3's "remain on the screen until the user takes an action": this was chosen in planning so an undo snack never holds the queue, and the screen already shows the result (the row is gone, the dot moved). This is the one deliberate departure from the guidelines.

Because only one snack is visible, the stacking problem (each top-layer popover placed at the same offset) disappears, and no stacking mechanism is added. The organizer console keeps `replace` mode (a new snack dismisses the shown one), which is also one at a time.

M3 also says snackbars "can be nudged upwards to avoid overlapping with other UI elements near the bottom, such as FABs" and "Don't animate other components along with snackbar animations". On Discovery the swap tile currently moves up when a snack opens (`--snack-stack-height`, `global.css`). It is reversed: while the tile is shown, Discovery publishes the distance from the viewport bottom to the tile's top edge as a bottom clearance (the same CSS-only pattern as `--bottom-banner-height`), and the snack bar uses it, plus one `space-3xs` step, in place of its navigation-and-banner offset. The tile sits in the route area, which already ends above any banner, so the clearance always exceeds the banner offset. The tile's margin no longer depends on the snack. `--snack-stack-height` goes.

Alternatives:
- Stack three snacks with CSS anchor positioning. It works only oldest-lowest (an anchor must be "in a lower top layer", [css-anchor-position-1](https://drafts.csswg.org/css-anchor-position-1/#acceptable-anchor-element)) and contradicts M3's "Don't stack snackbars".
- Keep snacks with an action until the fan acts, as M3 recommends. With one snack at a time, three hype changes would each wait for a tap or a swipe.

### D4. Swipe to dismiss with scroll snapping

Inside each snack, a horizontal scroller holds three slots: an empty one, the snack's content, and another empty one, with `scroll-snap-type: x mandatory` and the content centred at rest. An `IntersectionObserver` on the content dismisses the snack when less than half of it is visible. This is the mechanism the bottom sheet already uses for its downward dismiss, so the browser provides momentum, snapping back and cancelation. `pointerdown` on the snack pauses its timer (the remaining time is kept); `pointerup` and `pointercancel` resume it. Under reduced motion the exit transition is already zero, so a swiped snack disappears at once.

Alternative: pointer events with a drag threshold and a velocity check. Rejected because it re-implements what scroll snapping does.

A swipe dismisses through the same path as every other dismiss, so `onDismiss` (an unfollow's undo commit) fires once.

Found while implementing:
- The observer dismisses when at most 10% of the surface is left in the scroller, not at 50%. Mandatory snapping already carries a release past half into a gutter and a shorter one back, so this keeps "past half" while not dismissing a fan who drags past half and back before letting go. Like the bottom sheet, a scroll counts only after the fan touched or scrolled the snack, so the initial centring never dismisses it.
- On a touch device the browser takes a drag over with `pointercancel`, which would resume the timer mid-swipe. The item therefore also pauses while the fan scrolls it and resumes on `scrollend` (where the browser reports it).
- The scroller reaches one `space-m` past the snack on every side (negative margin, `pointer-events: none` there) so the surface's shadow is not clipped; only the surface takes taps.
- The organizer console's `replace` mode now shows the new snack after the old one's exit motion, like the fan app; its two stories that ended when the snack closed now wait until it has left the document before axe runs (mid fade, its colours blend).
- A real swipe in the stories needs raw touch events through the DevTools protocol (`swipeSideways` browser command): `Input.synthesizeScrollGesture` does not scroll in headless Chromium.

### D5. All Nearby filter sheet and its launcher item

The `.nearby-filters` chip row is removed. A new `<nearby-filter-sheet>` (a `bottom-sheet`) holds two rows, area and period, each showing its value. A tap on a row closes the filter sheet and then opens the existing `user-home-selector` or `date-range-sheet`, so two sheets are never open at once. `DiscoveryRoute` registers `[filter, help]` while the view is `nearby` and `[help]` otherwise, re-registering on every view switch (the launcher replaces an owner's set). The filter item's `isOn` is "the effective area differs from the fan's home area, or the period is not the `week` preset", the spec's rule; an override equal to the home area reads as inactive.

The date label (`date-range-sheet`'s emitted `label`, localized as today) moves from the chip to the period row.

Found while implementing: `<nearby-filter-sheet>` reports the chosen row (`filter-row-chosen`) only on the bottom sheet's `sheet-hidden`, so the selector opens after the filter sheet has finished closing. `date-range-sheet`'s `range-changed` now carries `applied` (the tapped preset, or null for a custom range; absent on the initial emission), so only what the fan applied is kept; a custom range equal to a preset's dates is still not kept. The FAB filter item reuses `fabMenu.filter`.

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

`NearbyVisit` starts from it; applying a preset or an area writes it; applying a custom range writes `datePreset: null`, so the next visit starts from `week`. Choosing the fan's own home area writes `areaCode: null`. Every read and write is wrapped in `try`/`catch`, and an unreadable value starts from the defaults. The key is cleared with the other guest state when guest state is reset before sign-in or sign-up (as the guest home and help-seen flags are, i18n spec "Resetting guest state does not change the rendered locale"), and on sign-out (`SignedOut`), so a fan never inherits another person's area. The value holds only the fan's own input, which the frontend's review rule allows in storage.

### D7. Card state: hype from follows, journey from the journey store

`ConcertStore.toDateGroupsForLocation` takes the fan's `hypeByArtist` (from `FollowStore`, filled by `FollowService.List`, or from the device for a guest) and the journey map (`TicketJourneyStore`, filled by `TicketJourneyService.List`). A performer the fan follows gets their hype; any other performer gets `watch`, which `isHypeMatched` never matches. The journey map goes to `toDateGroups` as on the dashboard.

`NearbyVisit.cache` keeps the `ListByLocation` proximity groups (the RPC response) instead of converted date groups, so a change of hype or journey re-derives the cards without a request. `NearbyConcerts` watches `journeyStore.journeyMap` and `followStore.hypeByArtist` and re-derives, as `DashboardRoute.onJourneyMapChanged` and its hype watch do. A visit straight to `/discovery?view=nearby` calls `journeyStore.load()`, which returns an empty map for a guest without a request.

Found on production after v1.143.0: opened straight on `/discovery?view=nearby`, the view could run its first load before the signed-in fan's account arrived, read no home area and open the area selector over the view (a race that predates this change, in the branch for a person without a home). The app deliberately opens Discovery without waiting for the account (the bubbles read nothing of it), so the view's load now waits for `IUserHydration.ready`, which settles once the boot-time hydration has finished or failed; a guest or fan without a home is still asked.

`NearbyConcerts` calls `journeyStore.load()` on every attach, not only on a direct visit: the store has no "loaded" flag, and a failure is logged and leaves the cards without badges rather than blocking the list.

Values the cards show and where they come from: artist name and lane from `ConcertService.ListByLocation`; hype from `FollowService.List`; journey status from `TicketJourneyService.List`; purchased count from the purchased-ticket store, unchanged.

### D8. Storybook: every story renders, and route stories are allowed

- `.storybook/screenshot.ts` imports `vitest` at module load, and loading `vitest` outside its runner throws (`chai.use(JestChaiExpect)` reads the missing worker state). The fix moves the import inside the `MODE === 'test'` branch as `await import('vitest')`. Commit 7e9cd168 guarded only the call, so it never took effect.
- `FourStacked` becomes a queue story: it publishes four snacks and asserts that exactly one is open at any moment and that they appear in order.
- The frontend `AGENTS.md` story rule changes from "Do NOT story route/page components" to: a route may have stories when every store and RPC client it resolves is registered as a fake through `defineAureliaStory({ items })` and nothing reaches the network; canvas surfaces (`dna-orb`) stay excluded. Storybook's guidance supports this: a full page is a connected component, and rendering one "you need to mock the data or modules that the component depends on" ([Build pages with Storybook](https://storybook.js.org/docs/writing-stories/build-pages-with-storybook)). Extracting the table into a presentational component would also make it storyable, but the defect is the route's own layout (its scroll container), which a component story would not render.
- `my-artists-route.stories.ts` renders the route with 40 fake follows, scrolls `tbody` by 300 px, asserts the hit test of each header label, and compares a screenshot baseline made in the pinned container (`visual-baselines` skill).

## Risks / Trade-offs

- [Safari and Firefox may drop table semantics when table elements change `display`] → Check with VoiceOver on iOS Safari against production after release. If the table is announced as plain text, add explicit `role="table"`, `rowgroup`, `row`, `columnheader`, `rowheader` and `cell`.
- [A burst of snacks (several hype changes in a row) is shown one after another, up to 10 seconds each] → A sender's `replaceKey` already folds repeated snacks about one artist into one; a swipe clears the visible snack at once.
- [Swipe scrollers inside every snack add work to each snack] → One snack is open at a time.
- [Snack changes reach the organizer console] → Its snack stories (`console-consolesnackbar--*`) run in the same Storybook job.
- [A kept area override hides a later change of the home area] → Choosing the home area clears the override, and the filter item shows its active state while the area differs from the home area.

## Migration Plan

Frontend-only release with no data migration. The new storage key starts empty, so the first visit after release uses today's defaults. Rollback is a revert; the leftover storage key is ignored by the previous version.

## Production verification (2026-11-06, v1.143.0)

Run with Playwright against https://liverty-music.app as the prod E2E fan (`e2e-test-password@liverty-music.app`, home 東京都), Pixel 7 emulation, touch through the DevTools protocol; the account's follows, hype levels and journeys were restored afterwards (Liverty Music Band at Nearby, no journey).

- 3.6 (emulated phone, not a physical device): three hype changes on My Artists showed at most one snack at any frame, in publishing order; a sideways swipe dismissed the first and the next appeared 1.4 s later (exit motion included); with a snack open on Discovery the swap tile moved 0 px and the snack sat 4.1 px (`space-3xs`) above it.
- 5.3: a tracking journey set from the detail sheet showed its badge on the All Nearby card without a reload, and removing it removed the badge; none of the 22 cards (all artists the fan does not follow) was lit. The followed artist had no concert in the period, so a lit card was not seen on production (unit-tested).
- Stage header: 0 px from the page header.
- 4.6 (v1.143.1, opened straight on `/discovery?view=nearby`): no area selector opened; the stage header touched the page header; the filter item was off on Tokyo and 7日以内, on after 今週末 and 大阪府, both kept across a reload, and off again once restored (kept value `areaCode: null`).
