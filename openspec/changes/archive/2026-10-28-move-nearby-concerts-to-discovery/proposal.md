## Why

The All Nearby view lists every concert near the fan's area for a chosen period, including concerts of artists the fan does not follow yet. For a fan looking for a live show this weekend it is one of the most useful screens in the app, but the only way to reach it is the third item of the FAB action arc on the dashboard, filed between display tools (laser effect, filter, help). A fan who never opens the arc never finds it.

It also sits on the wrong screen. The dashboard tab is named Timetable and shows the concerts of the artists the fan follows; All Nearby mostly shows artists the fan does not follow yet, which is the job of Discovery. The fans who gain the most from it are new fans with few follows, and they are the ones whose timetable is still empty.

## What Changes

- **BREAKING (fan UI)** The All Nearby view moves from the dashboard to Discovery. The dashboard keeps only the timetable of followed artists; its FAB action arc loses the item that switched modes. The view itself keeps its behavior: area chip, date chip with the date-range sheet, the two-lane HOME/NEAR list, and the follow action in the concert detail sheet.
- Discovery gets a swap tile beside the orb, in the band below the bubbles' floor that bubbles never enter, so the bubble field keeps its full size. The tile's icon draws two arrows in a loop with the current view's glyph large over them and the other view's glyph as a small corner badge; a tap swaps the two with a spring animation, and the new view grows out of the tile.
- `/discovery?view=nearby` opens the All Nearby view directly. Switching views rewrites the address without adding a history entry. Discovery reopens on the view the fan used last on that device, except while the fan is onboarding, when it opens on the artist bubbles.
- When the dashboard timetable is empty, the empty state links to the All Nearby view next to the existing link to Discovery.
- The Discovery help sheet gets a section that explains the All Nearby view.

## Capabilities

### New Capabilities

- `stories/find-concerts-nearby`: a fan finds the concerts near their area in a period, including artists they do not follow, and follows an artist from one of them; composes ConcertUseCase.ListByLocation and FollowUseCase.Follow.

### Modified Capabilities

- `components/infrastructure/fan/web/route/discovery`: the swap tile, the view address and the remembered view, the All Nearby requirements moved in from the dashboard, and the bubble simulation pausing while the All Nearby view is shown. (Purpose edited directly in the main spec.)
- `components/infrastructure/fan/web/route/dashboard`: the All Nearby requirements are removed; the timetable windowing and the event-selection requirements no longer mention the two-lane All Nearby list; the empty timetable links to the All Nearby view. (Purpose edited directly in the main spec.)
- `components/infrastructure/fan/web/global/fab-menu`: the dashboard contributes three actions (beam toggle, filter, help); the beam toggle and the filter no longer depend on a dashboard mode.
- `components/infrastructure/fan/web/global/bottom-sheet`: the follow action in the event detail sheet belongs to the All Nearby view on Discovery instead of a dashboard mode.
- `components/infrastructure/fan/web/global/page-help`: the Discovery help content gains the All Nearby section.

Unchanged and why: `components/usecase/concert/list-by-location`, `components/entity/concert/list-by-location` and `components/usecase/follow/follow` keep their promises; the new story only composes them. `components/infrastructure/fan/web/global/user-home-selector` already states the All Nearby area selector as a route-local, session-only override, which stays true on Discovery.

## Impact

- frontend only. Dashboard route (remove the All Nearby state, template branches and FAB mode-switch action), Discovery route (swap tile, view state, URL and remembered view, physics pause), a new component that holds the All Nearby view moved out of the dashboard, the swap tile icon (inline SVG), the page-help Discovery section, and the ja/en translation bundles.
- No proto, backend, database or infrastructure change. `ConcertService.ListByLocation` and `FollowService.Follow` are called as today.
- One new key in the device's local storage for the remembered Discovery view.
