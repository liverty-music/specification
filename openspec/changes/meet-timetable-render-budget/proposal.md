## Why

`reduce-timetable-render-cost` removed the freeze: on the reference profile (4× CPU, production account, about 212 dates) a Timetable re-entry went from a 5.4 s stall to about 0.6 s, and a cold load from 9.4 s to about 1.4 s between data arrival and the first frame (≈ 1.06 s of that on the main thread). Both are still above the 200 ms bounds the dashboard spec sets: INP for re-entry ("Tab-switch re-entry does not freeze on rendering"), and main-thread time to render once the data arrives for a cold load ("First dashboard load render cost is reduced"). The page-load LCP is a separate measure and not one of these bounds. This change meets those bounds. It carries tasks 5.1 and 5.2 moved out of that change.

## What Changes

The after-traces recorded in the archived `reduce-timetable-render-cost` design (D0) attribute the remaining time.

- **Re-entry** (INP 602 ms, a single 511 ms task):
  - ≈ 100 ms is forced layout for the scroll restore;
  - 55 ms is template creation on each navigation;
  - ≈ 80 ms comes from a popover opened on attach and another forced style recalculation;
  - ≈ 280 ms is the window's render.
- **Cold load** (≈ 1.4 s):
  - 340 ms converts the response for every loaded date, though only a window is built;
  - 198 ms renders the window;
  - ≈ 530 ms is layout and paint across two frames.

Candidate work, to be decided in design:

- Convert only the dates the window needs, not the whole response.
- Restore the remembered position without a forced layout inside the tap's task.
- Defer surfaces opened on attach (the popover, the forced style read) out of the tap's task.
- Reduce the paint cost of the timetable's glow shadows and blurred sticky separators.
- Settle the window size and growth step from the new traces (former task 5.2).
- Re-take the reference-profile traces and record them (former task 5.1).

Out of scope: the page-load LCP (≈ 4.4 s, app start and image fetch), which is a separate concern.

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

<!-- To be decided in design: the bounds already live in components/infrastructure/fan/web/route/dashboard; this change may only implement them. -->

## Impact

- **Frontend only**: `concert-highway`, the dashboard route, the concert store's response conversion, and the timetable stylesheets.
- **Verification**: reference-profile traces, before and after, recorded in this change's design.
