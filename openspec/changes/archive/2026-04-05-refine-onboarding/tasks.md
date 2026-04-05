## 1. Fix artist-filter-bar bottom sheet layout

- [x] 1.1 Replace `<fieldset>` with `<section aria-labelledby="filter-sheet-title">` in `artist-filter-bar.html`
- [x] 1.2 Replace `<legend class="sheet-header">` with `<div class="sheet-header">` containing `<h2 class="sheet-title">`
- [x] 1.3 Add `aria-labelledby="filter-sheet-title"` to `<ul class="artists-list">` (omit `role="group"` — spec prohibits it on `<ul>`)
- [x] 1.4 Remove `fieldset` browser-default resets (`margin: 0; border: none;`) from `artist-filter-bar.css`
- [x] 1.5 Verify sheet snaps flush to viewport bottom in browser

## 2. Remove lane introduction from DashboardRoute

- [x] 2.1 Remove `LaneIntroPhase` type export from `dashboard-route.ts`
- [x] 2.2 Remove `laneIntroPhase` and `selectedPrefectureName` properties
- [x] 2.3 Remove `startLaneIntro()`, `advanceLaneIntro()`, `completeLaneIntro()`, `updateSpotlightForPhase()` private methods
- [x] 2.4 Remove `onLaneIntroTap()` public method
- [x] 2.5 Remove `laneIntroSelector`, `laneIntroMessage`, `isLaneIntroActive` getters
- [x] 2.6 Remove `isOnboardingStepDashboard` getter (no remaining callers)
- [x] 2.7 Remove `isCelebrationShown` getter and `setCelebrationShown()` method
- [x] 2.8 Remove `startLaneIntro()` call from `attached()`
- [x] 2.9 Simplify `onHomeSelected()` — remove `waiting-for-home` branch, keep only data reload
- [x] 2.10 Remove `@watch` decorators for `dateGroups.length` and `isLoading` (lane intro only)
- [x] 2.11 Remove `onboarding.deactivateSpotlight()` call from `onCelebrationDismissed()`
- [x] 2.12 Remove unused imports: `queueTask`, `watch`, `translationKey`

## 3. Remove lane intro i18n keys

- [x] 3.1 Remove `dashboard.laneIntro` block from `src/locales/ja/translation.json`
- [x] 3.2 Remove `dashboard.laneIntro` block from `src/locales/en/translation.json`

## 4. Verification

- [x] 4.1 Run `make lint` — no errors or warnings
- [x] 4.2 Run `npx tsc --noEmit` — no type errors
- [x] 4.3 Run `make test` — all tests pass
