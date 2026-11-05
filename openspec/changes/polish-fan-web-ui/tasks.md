# Tasks

Sections 1 to 5 are in the `frontend` repository. Section 6 is an OpenSpec edit made in `specification` at archive time and needs no implementation worktree.

## 1. frontend: Storybook renders every story, and routes may have stories

- [ ] 1.1 Move the `vitest` import in `.storybook/screenshot.ts` inside the `MODE === 'test'` branch as a dynamic import (design D8), and verify with `npx storybook dev` and Playwright that `shared-snackbar--four-stacked`, `shared-snackbar--info` and `components-stateplaceholder--loading` render without the `customEqualityTesters` error, and that `npm run test-storybook` still compares screenshots
- [ ] 1.2 Change the frontend `AGENTS.md` story-authoring rule to allow route stories whose stores and RPC clients are all fakes registered through `items`, keeping `dna-orb` excluded (design D8), and verify the paragraph reads so

## 2. frontend: My Artists header outside the scrolling list (route/my-artists)

- [ ] 2.1 Make the hype table a grid with subgrid rows and `tbody` as the only scroll container; drop `position: sticky` and `backdrop-filter` from `thead`; move the edit-mode bottom padding to `tbody` (design D1); verify `npm run lint:css` and the existing My Artists unit tests pass
- [ ] 2.2 Add `src/routes/my-artists/my-artists-route.stories.ts` with fake follow and user stores, covering "Header renders with 4 columns", "Header column alignment matches artist row dot positions", "Header remains visible during scroll" (scroll 300 px, hit-test each label, screenshot baseline from the pinned container), "Header stays clear while a row animates out" and "Table semantics are kept" (aria snapshot); annotate each with `@spec`; verify `npm run test-storybook` passes in both motion projects
- [ ] 2.3 Cover "Slider spans header dot columns" in the same story file at 320, 375 and 768 px widths and verify it passes
- [ ] 2.4 Run `npm run build && npm run verify:build-templates` and update `ROUTE_MARKERS` if the template change removed a marker

## 3. frontend: Snack bar motion, one at a time, and swipe (global/snack-bar, route/discovery)

- [ ] 3.1 Add the `<snack-item>` custom element that binds a `Snack`, shows its popover in `attached()`, and on dismiss hides it, waits for the exit animations' `finished` promise and dispatches `snack-exited`, on which `<snack-bar>` removes it; replace the `SnackItem` record and the `toggle`-based removal in `snack-bar.ts` (design D2); verify the existing `snack-bar.spec.ts` passes after updating "DOM cleanup after exit transition" to assert the element is still present 100 ms after `dismiss()` and gone after the transition
- [ ] 3.2 Replace the three-snack stack with one visible snack and a FIFO queue, `replaceKey` replacement and the update snack giving way (design D3); rewrite the `FourStacked` story as a queue story and add unit tests for "Multiple simultaneous snacks", "A second snack waits", "Waiting snacks keep their order", "An undo window is kept", "Replacing an earlier snack", "Dismissing a waiting snack" and "The update snack gives way"; verify `npm run test-storybook` and `make test`
- [ ] 3.3 Publish the Discovery swap tile's top edge as a bottom clearance for the snack bar and drop `--snack-stack-height`, so the snack sits above the tile and the tile no longer moves (design D3); verify a story or unit test for "A floating control stays in place", "A banner and a floating control are both visible" and the swap tile's "A snack bar is open" scenario
- [ ] 3.4 Add the swipe scroller and the hold-to-pause timer (design D4); add stories with `play` functions for "Swipe past the dismiss point", "Short swipe", "Holding pauses the timer", "Swipe on a snack that stays until the fan acts" and "Swipe under reduced motion" (tagged `reduced-motion`); verify both motion projects pass
- [ ] 3.5 Run the organizer console snack stories (`console-consolesnackbar--*`) and verify they pass unchanged
- [ ] 3.6 After release, open the deployed fan app on a phone, follow and unfollow artists to raise three snacks, and verify they appear one at a time, animate out, leave on a sideways swipe, and sit above the swap tile on Discovery; then restore the follows and hype levels the check changed

## 4. frontend: All Nearby filters from the launcher (route/discovery, global/fab-menu)

- [ ] 4.1 Add the device storage module for `StorageKeys.nearbyFilter` in `src/adapter/storage/` (design D6) with unit tests for read, write, a custom range writing `datePreset: null`, the home area writing `areaCode: null`, unavailable storage, and clearing on the guest-state reset and on `SignedOut`; verify `make test`
- [ ] 4.2 Add `<nearby-filter-sheet>` with the area and period rows, remove the chip row from `nearby-concerts.html`, and open `user-home-selector` / `date-range-sheet` from the rows after the filter sheet closes (design D5); add its stories (default, override set, custom range label); verify `npm run test-storybook`
- [ ] 4.3 Register `[filter, help]` from `DiscoveryRoute` on the All Nearby view and `[help]` on the bubbles, re-registering on each view switch, with `isOn` as in design D5; verify unit tests for "Discovery contributes its actions per view", "Switching Discovery's view replaces its actions" and "Filter item shows its active state"
- [ ] 4.4 Start `NearbyVisit` from storage and write it on every apply; verify unit tests for "A preset is kept for the next visit", "A custom range is not kept", "The device keeps nothing", "Area override is kept on the device", "Choosing the home area clears the override", "Signing in, signing up or signing out clears the kept filter" and "Area override for unauthenticated user"
- [ ] 4.5 Update the All Nearby strings (`allNearby.*`, ja and en at parity) for the filter sheet and its rows, and verify the i18n parity test passes
- [ ] 4.6 Run the deployed app after release with Playwright (production, signed in with a fan account): open `/discovery?view=nearby`, verify the stage header touches the page header, open the filter from the launcher, choose 今週末 and another area, reload, and verify both are kept

## 5. frontend: All Nearby cards show matched state and journey (route/discovery)

- [ ] 5.1 Pass `hypeByArtist` and the journey map to `toDateGroupsForLocation`, giving any performer the fan does not follow `watch` (design D7); verify `concert-store.spec.ts` cases for "Followed artist matched by hype and lane", "Artist the fan does not follow is never matched" and "Guest with no follows"
- [ ] 5.2 Keep the proximity groups in `NearbyVisit.cache`, re-derive cards on changes of `journeyStore.journeyMap` and `followStore.hypeByArtist`, and load the journey store on a direct visit; verify unit tests for "Journey badge shown" and "Journey or hype changed in the detail sheet"
- [ ] 5.3 After release, on the deployed app, set a journey on an All Nearby concert from the detail sheet and verify the badge appears on its card without a reload, and that only followed artists' cards are lit; then remove the journey the check set

## 6. specification: Purpose at archive

- [ ] 6.1 When archiving, change the Purpose of `components/infrastructure/fan/web/global/snack-bar` from "at most three at once in the fan app" to "one at a time in the fan app" in the archive commit, and verify `openspec validate --specs` passes
