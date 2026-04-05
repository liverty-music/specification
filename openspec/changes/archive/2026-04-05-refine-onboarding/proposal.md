## Why

The `artist-filter-bar` sheet is misaligned from the bottom of the screen due to a CSS layout bug introduced when the sheet content was refactored to use `<fieldset>/<legend>` — a HTML element pair with browser-special layout behaviour that breaks `display: flex` and `scroll-snap` height calculation. Separately, the lane introduction onboarding step adds friction without measurable value: it delays users from reaching the dashboard and its complex spotlight/state-machine logic is a maintenance burden.

## What Changes

- **Fix** `artist-filter-bar` bottom-sheet layout: replace `<fieldset>/<legend>` with `<section>/<h2>` + `role="group"`, resolving the scroll-snap misalignment and the "全て解除" button positioning bug
- **Remove** the lane introduction sequence from the onboarding flow: delete `LaneIntroPhase` type, all lane intro state/methods/getters, and associated i18n keys
- Simplify `onHomeSelected()`: remove the `waiting-for-home` branch — home selection now only triggers a data reload
- Remove unused imports (`queueTask`, `watch`, `translationKey`) from `dashboard-route.ts`

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `dashboard-artist-filter`: The bottom-sheet content structure changes from `<fieldset>/<legend>` to `<section>/<h2>` to fix the scroll-snap layout bug. The "Filter disabled during onboarding" requirement is unaffected (filter is still hidden during onboarding via `if.bind="!isOnboarding"`).
- `dashboard-lane-introduction`: **REMOVED** — the lane introduction sequence is no longer part of the onboarding flow. The `onboarding-celebration` capability is unaffected (celebration is still shown, now triggered directly after home selection when data is available, but this path no longer exists in practice since lane intro was the sole trigger).

## Impact

- `frontend/src/components/artist-filter-bar/artist-filter-bar.html` — structural change only
- `frontend/src/components/artist-filter-bar/artist-filter-bar.css` — remove `fieldset` browser-reset rules
- `frontend/src/routes/dashboard/dashboard-route.ts` — significant reduction: ~130 lines removed
- `frontend/src/locales/ja/translation.json` — remove `dashboard.laneIntro` key
- `frontend/src/locales/en/translation.json` — remove `dashboard.laneIntro` key
- No API changes, no backend changes, no protobuf changes
