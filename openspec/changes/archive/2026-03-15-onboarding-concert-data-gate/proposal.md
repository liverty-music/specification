## Why

The onboarding flow transitions users from Artist Discovery (Step 1) to Dashboard (Step 3) after concert searches complete, but does not verify that concerts were actually found. When `ConcertService/List` returns zero groups, the Dashboard renders an empty state, and the lane introduction sequence fails because its target elements (`[data-stage-home]`, `[data-live-card]`) do not exist in the DOM. This leaves the coach mark overlay stuck with click-blockers active, making the UI completely inoperable.

The root cause is a missing data gate: the spec requires "concert search results have been received" but not "concerts have been discovered." The search can complete successfully with zero results.

## What Changes

- Add a concert data verification gate to the Discovery page coach mark condition: require `ConcertService/List` to return at least 1 date group before activating the Dashboard coach mark
- Add a user-facing message when searches complete but no concerts are found, prompting the user to follow more artists
- Add a Dashboard-side fallback: if the user reaches the Dashboard during onboarding with zero concert data (e.g., via direct nav tap), skip the lane intro and advance to Step 4 (My Artists tab spotlight) gracefully
- Add a coach mark component safety net: when `findAndHighlight()` exhausts retries, fully deactivate (close popover, release scroll lock, clear anchor-name) instead of only hiding the element

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `onboarding-tutorial`: Step 1 completion condition changes from "search completed" to "search completed AND concerts found". Add Step 3 empty-data fallback scenario.
- `dashboard-lane-introduction`: Add graceful skip behavior when no concert data is available.
- `onboarding-spotlight`: Coach mark `findAndHighlight()` retry exhaustion must fully deactivate instead of partial hide.

## Impact

- **Frontend**: `discover-page.ts` (coach mark gate), `dashboard.ts` (lane intro skip), `coach-mark.ts` (retry exhaustion cleanup)
- **E2E Tests**: New test scenario for empty concert data on Dashboard
- **Unit Tests**: New tests for Discovery gate condition and Dashboard empty-data fallback
- **No backend changes**: The `ConcertService/List` API already returns empty groups correctly; this is purely a frontend flow control issue
