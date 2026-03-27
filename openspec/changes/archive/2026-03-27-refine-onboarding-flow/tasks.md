## 1. Fix Dashboard Layout

- [x] 1.1 Add `grid-template-areas: "header" "content"` to `dashboard-route.css` `:scope`
- [x] 1.2 Change `concert-highway`, `.loading-text`, `inline-error`, `state-placeholder` placement from `grid-row: 2; grid-column: 1` to `grid-area: content`

## 2. Fix i18n Key Resolution Bug

- [x] 2.1 Import `translationKey` from `entities/user.ts` into `dashboard-route.ts`
- [x] 2.2 Replace i18n key generation in `onHomeSelected()` (L200-202) with `translationKey(code)`
- [x] 2.3 Replace i18n key generation in `startLaneIntro()` (L248-252) with `translationKey(homeCode)`

## 3. Expand Coach-Mark Tap Area

- [x] 3.1 Change `coach-mark.ts` `onBlockerClick()` to call `this.onTap?.()`

## 4. Improve Home Selector Display Timing

- [x] 4.1 Remove the `needsRegion && isOnboardingStepDashboard` branch in `dashboard-route.ts` `attached()` that directly calls `homeSelector.open()`
- [x] 4.2 Unify `attached()` to always call `startLaneIntro()` when `isOnboardingStepDashboard` (`startLaneIntro()` handles `needsRegion` internally)

## 5. Enhance Celebration Visuals

- [x] 5.1 Increase `.celebration-text` font size to `var(--step-4)` or larger in `celebration-overlay.css`
- [x] 5.2 Change `font-weight` to `bold`
- [x] 5.3 Strengthen `text-shadow` glow effect (increase radius and alpha values)
- [x] 5.4 Add styling for `.celebration-sub-text` (differentiate size and color from primary)

## 6. Verification

- [x] 6.1 Confirm lint, type checking, and tests pass via `make check`
- [ ] 6.2 Manual browser test of full onboarding flow (discovery → dashboard → lane intro → celebration → free exploration)
