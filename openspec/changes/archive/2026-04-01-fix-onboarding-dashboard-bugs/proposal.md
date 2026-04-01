## Why

Onboarding flow on the dashboard page has three interacting bugs that create a broken first-time user experience: (1) page-help bottom-sheet auto-opens simultaneously with the celebration overlay, producing a dark, unreadable screen, (2) the `?` help icon appears at the bottom-left of the page instead of inside the page header, and (3) tapping the celebration overlay does not start the lane introduction coach-mark sequence, leaving the user stuck with no guidance.

## What Changes

- **Fix page-help auto-open scope**: `PageHelp.attached()` must only auto-open on Discovery and My Artists. Dashboard is permanently excluded via an `autoOpenPages` allowlist — no auto-open at all on Dashboard (not deferred, permanently excluded).
- **Fix `?` icon positioning on dashboard**: Move `<page-help>` inside the dashboard page header (matching the pattern used in my-artists-route).
- **Fix lane intro not starting after celebration**: The `loading()` method sets `showCelebration = true` before `attached()` runs, which causes `startLaneIntro()` to be skipped. After celebration is dismissed, lane intro must be triggered.
- **Add regression tests**: Unit tests for `PageHelp` auto-open gating and `DashboardRoute` onboarding orchestration. E2E test for the full onboarding-to-dashboard flow.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `onboarding-page-help`: Dashboard page SHALL NOT auto-open the help sheet; auto-open is restricted to Discovery and My Artists via an `autoOpenPages` allowlist
- `onboarding-celebration`: Celebration MUST NOT appear before lane intro; it appears only after `completeLaneIntro()` is called (AWAY phase tap)
- `dashboard-lane-introduction`: Lane intro runs immediately on Dashboard attach; `completeLaneIntro()` (after AWAY tap) triggers celebration — not the other way around

## Impact

- `src/components/page-help/page-help.ts` — auto-open gating logic
- `src/routes/dashboard/dashboard-route.ts` — onboarding orchestration order
- `src/routes/dashboard/dashboard-route.html` — page-help placement in template
- New/updated test files in `src/components/page-help/` and `src/routes/dashboard/`
