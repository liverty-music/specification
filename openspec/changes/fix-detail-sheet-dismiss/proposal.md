## Why

Onboarding Step 4 is broken: the concert detail sheet opens ON TOP of the coach mark overlay due to Popover API LIFO top-layer stacking, making the My Artists tab unreachable and the tutorial stuck. Additionally, the detail sheet's backdrop tap-to-dismiss is broken for ALL users because `[popover]::backdrop` has UA-enforced `pointer-events: none !important`, and the `<dialog>` element only covers the bottom portion of the screen (`inset: auto 0 0`).

## What Changes

- Fix top-layer stacking order during onboarding Step 4 so the coach mark popover renders ABOVE the detail sheet popover (re-show coach mark after detail sheet enters the top layer)
- Fix detail sheet dismiss for non-onboarding usage: switch from `popover="manual"` to `popover="auto"` which provides free light dismiss (Escape, click-outside, browser-integrated CloseWatcher for Android back button)
- Dynamically set `popover="manual"` during onboarding Step 4 (non-dismissible per spec) and `popover="auto"` otherwise
- Add `popstate` listener to close the detail sheet when the user navigates back (the sheet pushes a history entry via `history.pushState` but never listens for back navigation)

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `concert-detail`: Update dismiss scenario to use `popover="auto"` for light dismiss instead of manual backdrop click handling. Add `popstate`-based close. Clarify top-layer stacking requirement for Step 4 coach mark.
- `onboarding-tutorial`: Update Step 4 to specify that the coach mark popover must re-enter the top layer AFTER the detail sheet opens, ensuring correct LIFO stacking.

## Impact

- `frontend/src/components/live-highway/event-detail-sheet.ts` — popover mode switching, popstate listener, remove manual Escape/backdrop handlers
- `frontend/src/components/live-highway/event-detail-sheet.html` — dynamic popover attribute
- `frontend/src/components/live-highway/event-detail-sheet.css` — remove manual backdrop styles if replaced by auto behavior
- `frontend/src/components/coach-mark/coach-mark.ts` — add method to re-show popover (hide + show) for top-layer re-ordering
- `frontend/src/routes/dashboard.ts` — coordinate detail sheet open → coach mark re-show sequence at Step 4
