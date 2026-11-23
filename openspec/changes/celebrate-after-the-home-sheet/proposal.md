## Why

A guest who chooses the home area on arrival at the Timetable never sees the celebration's animation. The sheet closes only after the choice is saved, and the Timetable loads behind it. On a measured run the celebration overlay was active 200 ms after the tap and the headline's animation was over at about 900 ms, while the home-area sheet stayed on screen until about 1,600 ms. The fan sees the finished overlay appear as the sheet goes. The code already says it means otherwise ("so the celebration shows after the sheet has closed"), and the spec gates the celebration on the home area being chosen and the data loaded, but not on the sheet being gone.

## What Changes

- The celebration overlay (both tiers) opens only when no bottom sheet is on screen. When the Timetable becomes real while a sheet is still open, the decisions wait for the last sheet to close, then run in the same order as before: the celebration decision, then the onboarding completion latch.
- One scenario states it: "Celebration plays after the home-area sheet closes".

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `components/infrastructure/fan/web/global/celebration-overlay`: a new requirement, the celebration opens once no sheet is on screen.

## Impact

- **frontend**: `TimetableRoute.onTimetableReady` waits on `IBottomSheetTracker`; one unit test and one e2e test.
- No RPC, storage or proto change. A fan who leaves a sheet open sees the celebration, and the onboarding completion, after it closes instead of at once.
