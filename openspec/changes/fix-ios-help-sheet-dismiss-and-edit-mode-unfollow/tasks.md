## 1. Regression guard (WebKit) — land first, must be RED

- [ ] 1.1 Add `e2e/functional/page-help-sheet-webkit.spec.ts`: open the My Artists page-help sheet, sample `dialog.open` over ~1.5s, assert it stays open AND its content is visible (not merely `open`)
- [ ] 1.2 Add `webkit-repro` (real WebKit, iPhone 14) and `chromium-control` projects to `playwright.config.mjs`; exclude the spec from the Chromium `functional` project
- [ ] 1.3 Confirm the guard is RED on `webkit-repro` and GREEN on `chromium-control` before the fix (`npx playwright test --project=webkit-repro --project=chromium-control`)

## 2. Bottom-sheet dismiss fix (`bottom-sheet-ce`)

- [ ] 2.1 Make `scrollsnapchange` (`onSnapChange`) the primary swipe-dismiss signal in `bottom-sheet.ts`
- [ ] 2.2 Delete the `onScrollEnd` (`scrollRatio < 0.1`) and `onPointerUp` (`scrollTop/max < 0.25`) scroll-ratio dismiss heuristics and their template bindings
- [ ] 2.3 Add an `IntersectionObserver` fallback for engines without `scrollsnapchange` (Firefox), armed only after the sheet settles on `.sheet-body`
- [ ] 2.4 Add a "just-opened" dismiss guard that suppresses all dismiss signals until the sheet settles on `.sheet-body`
- [ ] 2.5 Correct the stale "Safari lacks `scrollsnapchange`" comment; keep the CSS `initial-snap` trick unchanged
- [ ] 2.6 Ensure detach cleanup disconnects the `IntersectionObserver` and removes the `scrollsnapchange` listener
- [ ] 2.7 Run the guard again: `webkit-repro` MUST now be GREEN; verify sheet content is visible (add a one-line deterministic `scrollTop = maxScroll` on settle only if the test shows it parking blank)

## 3. Edit-mode unfollow (`edit-mode-unfollow`)

- [ ] 3.1 Add an "Edit" toggle control in the `page-header` slot (trailing, beside `<page-help>`) with an `editing` state on the route; toggle label reflects state (Edit ↔ Done)
- [ ] 3.2 Reveal a per-row remove (−) control in edit mode; hide it otherwise; no persistent per-row control in the default list on any pointer type
- [ ] 3.3 Show the Edit toggle only in the populated state; hide it while loading and in the empty (zero-artist) state
- [ ] 3.4 Edit-mode lifecycle: auto-exit when the last artist is removed; do not persist edit state across navigation (fresh non-editing on re-entry); keep hype controls interactive while editing
- [ ] 3.5 Wire the remove control to the existing `unfollowArtist()` flow (immediate optimistic removal + Undo), preserving the onboarding guard
- [ ] 3.6 Accessibility: Edit toggle is a keyboard-operable button exposing `aria-pressed`; each remove control has an accessible name identifying the artist (e.g., "Unfollow {name}")
- [ ] 3.7 Ensure the remove control is a single-tap target on both `pointer: coarse` and `pointer: fine` (min 44px touch target); style per CUBE CSS, no inline styles
- [ ] 3.8 Add unit/E2E coverage: entering/leaving edit mode, toggle hidden when empty/loading, remove-unfollow, Undo restore, auto-exit on last removal, edit state not persisted across nav, onboarding block

## 4. Remove long-press unfollow (`long-press-unfollow` retired)

- [ ] 4.1 Delete `frontend/src/custom-attributes/long-press.ts` and its registration in `main.ts`
- [ ] 4.2 Delete the `ArtistUnfollowSheet` component (`artist-unfollow-sheet.{ts,html,css}`) and its usage in `my-artists-route.html`
- [ ] 4.3 Remove the long-press binding, `openUnfollowSheet`/`unfollowSheetOpen` wiring, and `selectedArtistForUnfollow` from `my-artists-route.{ts,html}`
- [ ] 4.4 Remove the always-visible trash column entirely for all pointer types (the `.artist-unfollow-col` cell, the `@media (pointer: coarse) { display:none }` rule, and the visually-hidden `myArtists.table.unfollowCol` header if no longer applicable), unified onto Edit mode
- [ ] 4.5 Delete the long-press unit tests and any `long-press` E2E references

## 5. Help content (`my-artists` / page-help)

- [ ] 5.1 Replace the page-help "long press to unfollow" section with Edit-mode guidance; remove the `isPointerCoarse` gate on that section if no longer needed
- [ ] 5.2 Replace `longPressTip` i18n keys with Edit-mode copy in both `ja` and `en`; remove orphaned keys

## 6. Verification

- [ ] 6.1 `make check` (Biome lint + format + stylelint + typecheck + brand-vocabulary + unit tests) passes
- [ ] 6.2 Full Playwright suite passes, including `webkit-repro` GREEN and `chromium-control` GREEN
- [ ] 6.3 Manual real-iOS-device check: help sheet opens and stays open; Edit-mode unfollow + Undo works

## 7. Ship to production

- [ ] 7.1 Open the frontend PR; wait for all CI checks to complete green; address review; merge to `main`
- [ ] 7.2 Cut a frontend GH Release (SemVer tag) → prod AR retag → automated pin-bump → ArgoCD sync
- [ ] 7.3 Confirm the release deployed to prod (workflow runs green; new pin live)

## 8. Post-ship & archive readiness

- [ ] 8.1 Verify the two defects are resolved on prod (real iOS device)
- [ ] 8.2 Sync delta specs to main specs, then archive the change (`edit-mode-unfollow` created, `long-press-unfollow` removed, `bottom-sheet-ce` + `my-artists` updated)
