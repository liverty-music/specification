## 1. frontend: wait for the open sheets (global/celebration-overlay; design D1 to D3)

- [ ] 1.1 In `TimetableRoute.onTimetableReady`, wait while `IBottomSheetTracker.openCount > 0` and run the celebration decision and the completion latch together once it is 0; check the conditions again then and drop the wait in `detaching()`; verify a unit test for "Celebration plays after the home-area sheet closes" and one for leaving the route while waiting
- [ ] 1.2 Add an e2e test in `onboarding-flow.spec.ts` that samples every frame after the home area is chosen and asserts no frame has the sheet open and the celebration active; verify it fails without 1.1 and passes with it
