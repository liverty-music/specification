## Context

`TimetableRoute.onHomeSelected` saves the home area, sets `needsRegion = false` and starts `loadData()` without awaiting it. Resolving the promise lets the home-area sheet start closing, and `<bottom-sheet>` reports closed to `IBottomSheetTracker` only after its close has finished. The data load usually settles first, `timetableLoadedChanged` calls `onTimetableReady`, and `maybeCelebrate` opens the overlay while the sheet is still there. The overlay sits below the sheet's top layer, so its entrance plays unseen.

## Decisions

### D1. Wait for the tracker, not for the home-area sheet only

`onTimetableReady` returns while `IBottomSheetTracker.openCount > 0`, and re-runs when the count reaches 0 (the tracker's `onChange`). Any sheet counts: the help sheet, a concert's detail sheet or the home-area sheet. The overlay would play under any of them, and guide moments already wait on the same tracker. Waiting only for the home-area sheet would need a second signal for the same fact.

Alternative rejected: delay the celebration by a fixed time. The sheet's close time depends on the device and the motion setting.

### D2. The celebration decision and the completion latch wait together

The latch is evaluated after the celebration decision so that the decision still sees the fan in onboarding. Waiting for only one would let the latch finish onboarding first and suppress the celebration.

### D3. Conditions are checked again when the wait ends

The route may have started a new load or lost its region while it waited, so the deferred run checks `timetableLoaded`, `needsRegion` and `isLoading` again, and leaving the route drops the wait (`detaching`).

## Risks

A sheet left open indefinitely (a fan who opens Help and reads) delays the celebration and the completion latch until it closes. Both are decisions about the Timetable the fan is looking at, so this is the intended order.
