## Why

Onboarding flow on the dashboard page has three interacting bugs that create a broken first-time user experience: (1) page-help bottom-sheet auto-opens simultaneously with the celebration overlay, producing a dark, unreadable screen, (2) the `?` help icon appears at the bottom-left of the page instead of inside the page header, and (3) tapping the celebration overlay does not start the lane introduction coach-mark sequence, leaving the user stuck with no guidance.

## What Changes

- **Fix page-help auto-open race condition**: `PageHelp.attached()` must not auto-open when celebration overlay or lane intro is active. Defer auto-open until celebration is dismissed.
- **Fix `?` icon positioning on dashboard**: Move `<page-help>` inside the dashboard page header (matching the pattern used in my-artists-route).
- **Fix lane intro not starting after celebration**: The `loading()` method sets `showCelebration = true` before `attached()` runs, which causes `startLaneIntro()` to be skipped. After celebration is dismissed, lane intro must be triggered.
- **Add regression tests**: Unit tests for `PageHelp` auto-open gating and `DashboardRoute` onboarding orchestration. E2E test for the full onboarding-to-dashboard flow.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `onboarding-page-help`: Auto-open must be suppressed while celebration overlay or lane intro is active
- `onboarding-celebration`: Celebration dismiss must trigger lane intro sequence instead of entering free exploration directly
- `dashboard-lane-introduction`: Lane intro must start after celebration dismiss when arriving from discovery during onboarding

## Impact

- `src/components/page-help/page-help.ts` — auto-open gating logic
- `src/routes/dashboard/dashboard-route.ts` — onboarding orchestration order
- `src/routes/dashboard/dashboard-route.html` — page-help placement in template
- New/updated test files in `src/components/page-help/` and `src/routes/dashboard/`
