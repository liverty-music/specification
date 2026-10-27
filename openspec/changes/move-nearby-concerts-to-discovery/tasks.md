All tasks are in the frontend repository. Every test that covers a spec scenario carries the `@spec <capability> "<scenario>"` annotation the scenario-coverage check reads.

## 1. Swap tile (components/infrastructure/fan/web/route/discovery — "Swap tile switches between the artist bubbles and the All Nearby view")

- [ ] 1.1 Build the `discovery-swap-button` component per design D3 (inline SVG with the generated arrow paths, both glyphs, the two slots, token colours, CSS-only motion with the accumulated `--ring-turn`, sparkles as a CSS animation) and verify with component tests that cover "Switching to the All Nearby view" and "Switching back to the artist bubbles" (glyph sizes, badge, label 「アーティスト」/「近くのライブ」, accessible name) and "Reduced motion" (no transition or animation under `prefers-reduced-motion: reduce`).
- [ ] 1.2 Publish `--snack-stack-height` on `:root` while a snack is open, next to the `--fab-sunk` rule in `global.css`, and verify that the FAB tests still pass and that a component test shows the tile's block-end offset grows by the snack height ("A snack bar is open").

## 2. All Nearby view moved into its own component (discovery — the moved All Nearby requirements)

- [ ] 2.1 Extract `<nearby-concerts>` from the dashboard per design D4 (area override, date range, per-visit cache passed in by the route, `loadAllNearby()` and its abort, two-lane highway, empty state, area selector, date-range sheet, event selection) and port the All Nearby cases of `dashboard-route.spec.ts` into its own spec; verify they pass for "All Nearby result cached independently", "Cache invalidated on filter change", every scenario of "Date Preset Selector in the All Nearby View", "Area Selector in the All Nearby View", "Compact All Nearby Filter Bar on Discovery" and "Localized All Nearby Date Display on Discovery".
- [ ] 2.2 Cover "All Nearby Concert List" in the same spec: "HOME and NEARBY lanes rendered", "Venue name shown for all lanes", "Empty state" (no Discovery link; chips stay), "First-party concert opens its event page" and "Closing the detail sheet returns to the list" (address is `/discovery?view=nearby` after close, the area, range and scroll position are kept); fix the sheet's address capture if the last one fails, and verify the spec passes.
- [ ] 2.3 Add the tile labels (`discovery.swap.toNearby` 「近くのライブ」/"Near you", `discovery.swap.toArtists` 「アーティスト」/"Artists") and keep every `allNearby.*` key in both bundles; verify the i18n parity test covers "All Nearby strings are natural Japanese".

## 3. Discovery route (discovery — view switching, address, pause; page-help)

- [ ] 3.1 Add the view state per design D5 (`view` query, `StorageKeys.discoveryView` through the storage adapter, onboarding override, `replaceState` sync) and verify route unit tests for "Link to the All Nearby view", "Switching rewrites the address", "The last view is remembered", "Onboarding opens on the artist bubbles" and "The device keeps nothing".
- [ ] 3.2 Place the tile and `<nearby-concerts>` in `discovery-route.html` per design D2, D6 and D7 (orb-band position, left-handed mirror, hidden in search mode, `switchView()` with the View Transition reveal, `pause()`/`resume()`), and verify unit tests for "All Nearby view pauses the simulation" (MODIFIED "Bubble physics pauses when Discover tab is inactive", with its existing scenarios still passing), "Search mode" and "Left-handed mode".
- [ ] 3.3 Add `e2e/functional/discovery-swap.spec.ts` and run it with Playwright against a local build (`npx playwright test e2e/functional/discovery-swap.spec.ts`): "The tile never covers the bubble field" (375 px viewport, orb at its largest, tile centre 260–300 px, no bubble under the tile, bubble area height equal with and without the tile), switching both ways, "A snack bar is open" and "The FAB menu is open"; verify it passes.
- [ ] 3.4 Add the "近くのライブ" / "Near you" section to the Discovery page help between the two existing sections, and verify the page-help test for "Discovery help content" (MODIFIED "Page-specific Help Content") renders three sub-sections in that order.

## 4. Dashboard and shared surfaces (dashboard, fab-menu, bottom-sheet)

- [ ] 4.1 Remove the All Nearby code from the dashboard per design D8 (view state, `isAllNearby` branches, chip row, second home selector, date-range sheet, mode-swap FAB action) and verify `dashboard-route.spec.ts` passes for "Event selection handled by dashboard", "First-party concert opens its event page", "Back from the event page" and "Loading and empty states" (MODIFIED "Dashboard routes event selection and shows its loading states").
- [ ] 4.2 Move the two-lane cases of `e2e/functional/timetable-window.spec.ts` to the Discovery All Nearby view, keep the three-lane cases on the dashboard, and verify it passes for every scenario of the MODIFIED "The timetable renders a window of dates around the fan".
- [ ] 4.3 Add the 「近くのライブを見る」 link to both dashboard empty states (`dashboard.nearbyCta`) and verify tests for "Guest with no follows", "Followed artists with nothing to show" and "Timetable with concerts" (ADDED "Empty timetable offers the All Nearby view").
- [ ] 4.4 Update `e2e/functional/fab-menu-arc.spec.ts` and the FAB unit tests to the dashboard's three actions and verify they pass for "Labels never overlap icons", "Dashboard contributes its actions", "Within-route mode change replaces, not accumulates", "Toggle button placement and icon" and the filter scenarios of "Filter chip UI in page header".
- [ ] 4.5 Update the event-detail-sheet tests to the All Nearby view on Discovery and verify every scenario of the MODIFIED "Follow CTA in Event Detail Sheet" passes, including "Follow button hidden in My Timetable context" opened from the dashboard timetable.

## 5. Story (stories/find-concerts-nearby)

- [ ] 5.1 Add the E2E test for "A weekend near home", "No home area yet", "Signed-in fan follows from a nearby concert" and "Guest taps follow" with the RPC fixtures the functional suite uses, and verify it passes against a local build.

## 6. Integration

- [ ] 6.1 Run `make check` in the frontend and verify it passes; open the PR citing this change.
- [ ] 6.2 After the release reaches production, open Discovery on a phone, switch to the All Nearby view and back with the tile, open a concert and close it, and confirm the address and the view; confirm the dashboard FAB shows three actions. Record the result in this file.
