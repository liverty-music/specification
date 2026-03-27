## Why

The onboarding experience after transitioning from discovery to the dashboard has multiple defects. Internal variable names are exposed in the UI, the tappable area is limited to the spotlight target only, the celebration overlay lacks visual impact, and the dashboard layout is broken. These issues significantly harm the first impression for new users and require immediate fixes.

## What Changes

- **Fix i18n key resolution bug**: Numeric-based i18n keys like `userHome.prefectures.40` are exposed raw in the UI. Use the existing `translationKey()` helper to resolve the correct prefecture name
- **Expand coach-mark tap area**: During the stage intro, only the spotlight target was tappable. Change to allow tapping anywhere on the screen to advance
- **Enhance celebration visuals**: Increase text size, weight, and glow effects to create a stronger sense of accomplishment
- **Fix dashboard layout**: Add missing `grid-template-areas` to resolve page-header width collapse bug
- **Improve home selector timing**: Instead of showing the home selector immediately on dashboard entry, display it within the lane intro context

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `dashboard-lane-introduction`: Expand coach-mark tappable area to full screen, improve home selector display timing, fix i18n key resolution bug
- `onboarding-celebration`: Enhance celebration text visual prominence
- `page-header-ce`: Fix missing `grid-template-areas` in dashboard-route (page-header component itself is unchanged; fix is on the consumer side)

## Impact

- **frontend/src/routes/dashboard/dashboard-route.ts**: Fix i18n key resolution logic, adjust home selector display timing
- **frontend/src/routes/dashboard/dashboard-route.css**: Add `grid-template-areas`
- **frontend/src/components/coach-mark/coach-mark.ts**: Add tap-to-advance on `onBlockerClick()`
- **frontend/src/components/celebration-overlay/celebration-overlay.css**: Enhance text visual effects
- **frontend/src/locales/**: Update translation files if text content changes
