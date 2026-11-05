## Why

Four surfaces of the fan app do not behave as their specs or the fan expect, and each traces to a mechanism that is wrong rather than missing:

- My Artists' hype header scrolls with the rows it labels. It is `position: sticky`, but every row paints over it: each row carries a `view-transition-name` (a stacking context) and positioned dots, and `z-index` is banned by the stylesheet lint. Measured in Chromium with the real stylesheet, the element under the header's labels after scrolling is a row's dot.
- Snack bars never animate out, and several snacks overlap in one place. The snack bar removes a snack on the popover's `toggle` event, which fires the moment `hidePopover()` is called (measured: 0 ms), not when the exit transition ends (490 ms later), so the element leaves the DOM before its transition plays. Up to three snacks are shown at once, but each is its own top-layer popover with the same bottom offset: three open snacks measured at the same top and bottom edges. Material 3 shows one snackbar at a time and never stacks them. Snacks also cannot be swiped away, and on Discovery the swap tile moves up for a snack, where Material 3 moves the snack instead.
- Discovery's All Nearby view puts a row of filter chips above the stage header, where the dashboard has none, and forgets the area and period on every visit.
- All Nearby cards show no journey badge, and every card looks matched. The view builds its cards with an empty journey map and gives every performer the default hype level Nearby, which matches both the HOME and the NEAR lane.

Two tooling faults hide this class of defect: route components may not have stories, so a route's layout is never rendered in Storybook, and 11 of the 59 stories do not render in the Storybook UI at all, because a shared screenshot helper imports `vitest` at module load, which throws outside the Vitest runner.

## What Changes

- My Artists: only the list body scrolls; the hype header stays outside the scroll area, in the same table, its columns aligned with the rows. No stacking order is needed, so the `z-index` ban stays.
- Snack bar: a snack stays in the DOM until its exit motion ends; one snack is shown at a time and the others wait in order, as Material 3 says (a snack with an action keeps its 10-second time); the app update snack gives way to other snacks; a horizontal swipe dismisses a snack, and a touch pauses its timer; on Discovery the snack sits above the swap tile, which no longer moves. Each snack is rendered by a component that takes the published `Snack` as its model instead of a copied record.
- All Nearby: the area and date chips go; the stage header sits directly under the page header, as on the dashboard. The FAB launcher's new filter item opens one sheet for the area and the period, and shows its active state when either differs from the default. The chosen area and date preset are kept on the device for the next visit; a custom range is not kept.
- All Nearby cards: a followed artist's card is matched by the dashboard's hype-and-lane rule, an artist the fan does not follow is never matched, and a concert with a journey shows the dashboard's journey badge, updated when the journey or hype changes.
- Storybook: every story renders in the Storybook UI; the four-snack story asserts that the open snacks do not overlap; route components may have stories when every store and RPC client they use is replaced with a fake, and My Artists gets one that compares the scrolled list with a baseline.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `components/infrastructure/fan/web/route/my-artists`: the hype header stays outside the scrolling list (replaces "Sticky Header Legend", which prescribes `position: sticky`); dot alignment is stated as an outcome instead of a column template.
- `components/infrastructure/fan/web/global/snack-bar`: removal waits for the exit motion; one snack at a time (replaces "At most three snacks are shown at once"); the snack sits above a floating control; swipe to dismiss and touch to pause.
- `components/infrastructure/fan/web/route/discovery`: All Nearby filters open from the launcher instead of chips (removes "Compact All Nearby Filter Bar"; replaces "Date Preset Selector in the All Nearby View" and "Area Selector in the All Nearby View" with requirements that keep the preset and the area on the device); cards show matched state and journey by the dashboard's rules; the date label moves from the chip to the filter sheet.
- `components/infrastructure/fan/web/global/fab-menu`: Discovery contributes a filter action while the All Nearby view is shown.

## Impact

- Frontend only: `src/routes/my-artists/`, `shared/ui/snack-bar/` (shared with the organizer console, which gets the same motion and swipe and keeps its replace mode), `src/components/all-nearby/`, `src/routes/discovery/discovery-route.ts`, `src/services/concert-store.ts`, `src/adapter/storage/`, `.storybook/screenshot.ts`, `shared/ui/snack-bar/snack-bar.stories.ts`, a new My Artists route story, and the frontend `AGENTS.md` story-authoring rule.
- No proto, backend or infrastructure change. No dev environment is needed: Storybook (both motion projects), unit tests and read-only production checks verify it.
- The artist detail sheet that the same request asked for is a separate change (`show-artist-detail-sheet`), because it needs a new RPC and backend data.
