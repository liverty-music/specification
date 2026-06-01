## 1. Reset behavior (BubbleManager)

- [x] 1.1 Add a `reset()` method to `BubbleManager` that clears seen-sets, fetches `listTop(country, '', 50)`, dedups against followed artists, caps at 50, replaces the pool, and re-tracks seen
- [x] 1.2 Ensure `reset()` discards prior eviction history so the new field is a clean baseline
- [x] 1.3 Reload the canvas after reset so physics bodies match the new pool (pool count == physics count)
- [x] 1.4 (QA-discovered) Top up `loadInitialArtists` with global top artists when the deduplicated seed-similar results fall below a target (30), keeping similar artists first — the field was shrinking as follow count grew (11 follows → 14 bubbles); now stays full (→ 35) and is never empty

## 2. Reset orchestration (DiscoveryRoute / GenreFilterController)

- [x] 2.1 Add an `onReset()` handler on `DiscoveryRoute` that clears `genre.activeTag`, invokes `bubbles.reset()`, and calls `dnaOrbCanvas.reloadBubbles(...)`
- [x] 2.2 Reuse the existing genre-deselect reload path where practical to avoid duplicate logic
- [x] 2.3 Guard against concurrent reloads (respect `isLoadingTag` / loading flags) and the abort signal

## 3. Reset control (template + styles)

- [x] 3.1 Add an icon-only (⟳) reset `<button>` as the leading item of the genre row in `discovery-route.html`, wired to `onReset()` with an i18n `aria-label`
- [x] 3.2 Add the `rotate-ccw` reset icon to the svg-icon set
- [x] 3.3 Style the reset control as a flex sibling beside the scrollable chips (no z-index — moved out of the scrolling fieldset to stay visible without overlap)
- [x] 3.5 (QA-discovered) Define the discovery grids explicitly with named `grid-template` areas + `minmax(0, 1fr)` column (per the app-shell-layout / page-header-ce grid-area rule). The unconstrained `auto` column had blown out to the chip row's max-content (~798px) and was clipped by `overflow:hidden`, pushing the search bar and orb off-screen; `.discovery-layout` now declares `"search"/"genre"/"bubbles"` areas with children placed via `grid-area`
- [x] 3.4 Add i18n keys for the reset aria-label in `en` and `ja` translation files

## 4. Type-scale floor + migration

- [x] 4.1 Raise `--step--2` in `tokens.css` to `clamp(0.6875rem, calc(0.6rem + 0.13vi), 0.7rem)` (11px floor, min-only)
- [x] 4.2 Migrate `--step--2` → `--step--1` in: discovery `.genre-chip`, artist-filter-bar, page-help, user-home-selector, concert-highway, event-card (×2), event-detail-sheet (×2), post-signup-dialog, inline-error (×2), error-banner (×2), tickets-route `--_size-hint`, settings-route (×4), consent-route (×2)
- [x] 4.3 Leave `--step--2` in place for `bottom-nav-bar` and `.hype-col-header` (incl. its `& small`); add a brief CSS comment noting the compact-only exception

## 5. Validation & QA

- [x] 5.1 Run `make lint` (biome + stylelint + typecheck) and resolve any findings — 0 errors (only pre-existing warnings remain)
- [x] 5.2 Add unit tests for `BubbleManager.reset()` (pool replaced with top artists, followed excluded, seen-sets cleared) — `bubble-manager.spec.ts`, 3 tests
- [x] 5.3 Run `make test` — 106 files / 1148 tests pass
- [x] 5.4 Manual QA: reset returns to Top 50, clears active genre; verify bottom-nav labels and my-artists hype table still look correct at the new font sizes — verified locally via Playwright (full stack on :8080/:9000); reset clears Pop filter + restores Top 50, chips legible at --step--1, nav labels compact, 0 console errors
- [x] 5.5 Confirm no `--step--2` consumers remain outside the two documented exceptions (`grep`)

## 6. Ship

- [x] 6.1 Open frontend PR, get CI green, address review, merge to main — frontend#394 merged (CI green after refreshing the visual baselines for the intentional font diff); spec change in specification#556
- [x] 6.2 Cut the frontend prod release and bump the cloud-provisioning prod pin so the change ships to prod — GH Release v1.4.0 (retag dev→prod AR), cloud-provisioning#338 (prod pin v1.3.4→v1.4.0 + version label), ArgoCD synced prod to web-app:v1.4.0 (Healthy), verified live at liverty-music.app. (Dev verification skipped — dev env intentionally stopped; verified directly on prod.)
