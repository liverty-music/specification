## Why

`ScanDueReminders` can send a sales-phase reminder after its moment has already passed (an "1 hour left to apply" push after the deadline, or a lottery-result push days after the result day), and its quiet-hours fallback for a deadline stage fires the pre-quiet alert exactly at 22:00 — the first instant of the quiet window it exists to avoid. Both are spec/implementation gaps found by an audit of `usecase/sales-phase/scan-due-reminders` and `stories/get-reminded-of-ticket-sale-milestones` against the shipped code (`liverty-music/backend#472`), which the specs already flag with `Known defect: liverty-music/backend#472` notes.

## What Changes

- `scan-due-reminders`: add an explicit upper bound (expiry) per stage, so a stage already past its moment is never requested, not even on a fan who starts tracking late or a delayed scan run:
  - `APPLY_CLOSE_24H` / `APPLY_CLOSE_1H`: unchanged — already specified as never at or after the apply end time (this scenario already passes; documented here for completeness).
  - `APPLY_OPEN`: never requested once the apply end time has passed, when known.
  - `RESULT_DAY`: never requested after the end of the calendar day, in the fan's time zone, of the lottery result time.
- `scan-due-reminders` quiet hours: the pre-quiet fallback for a deadline stage moves from 22:00 (the start of the quiet window) to 21:00 (one hour before it), so the alert itself always lands outside quiet hours. If 21:00 is not strictly before the apply end time, there is no valid moment left outside quiet hours before the deadline and the stage is not requested for that run.
- `get-reminded-of-ticket-sale-milestones` (story): update the "No reminder at night" requirement's wording to match (before 21:00, not 22:00) and remove the resolved `Known defect: liverty-music/backend#472` note.

## Capabilities

### New Capabilities

- (none)

### Modified Capabilities

- `components/usecase/sales-phase/scan-due-reminders`: the "A stage is requested once its due time has passed" requirement gains explicit expiry rules for `APPLY_OPEN` and `RESULT_DAY`; the "Quiet hours" requirement's pre-quiet fallback moves from 22:00 to 21:00 and gains a "no valid slot" case; the resolved `Known defect` note is removed.
- `stories/get-reminded-of-ticket-sale-milestones`: the "No reminder at night" requirement's wording changes from "before 22:00" to "before 21:00"; the resolved `Known defect` note is removed.
- Relies on (unchanged): `components/entity/sales-phase` (attributes `apply_end_at`, `lottery_result_at`, `discovered_at` already exist and are unchanged) and `components/entity/sales-phase-reminder/list-sent-stages` (unchanged — this fix only tightens when `ScanDueReminders` decides a stage is still eligible, not how sent stages are read).

## Impact

- **Code**: `backend/internal/usecase/sales_reminder_uc.go` (`scheduledFireTime` gains an expiry return value; `processPhase` gates on it; the pre-quiet fallback hour changes from `quietStartHour` to `quietStartHour - 1`). No proto, API, or DB schema changes.
- **Tests**: table tests for `scheduledFireTime`'s new expiry values and the shifted pre-quiet hour; `ScanDueReminders`-level tests for an expired phase (no stage requested) and a not-yet-expired phase (still requested).
