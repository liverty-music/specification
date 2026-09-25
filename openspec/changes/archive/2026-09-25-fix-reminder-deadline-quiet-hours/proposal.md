## Why

`ScanDueReminders` can send a sales-phase reminder after its moment has already passed (an "1 hour left to apply" push after the deadline, or a lottery-result push days after the result day), and its quiet-hours fallback for a deadline stage fires the pre-quiet alert exactly at 22:00 — the first instant of the quiet window it exists to avoid. Both are spec/implementation gaps found by an audit of `usecase/sales-phase/scan-due-reminders` and `stories/get-reminded-of-ticket-sale-milestones` against the shipped code (`liverty-music/backend#472`), which the specs already flag with `Known defect: liverty-music/backend#472` notes.

## What Changes

- `scan-due-reminders`: add an explicit upper bound (expiry) per stage, so a stage already past its moment is never requested, not even on a fan who starts tracking late or a delayed scan run:
  - `APPLY_CLOSE_24H` / `APPLY_CLOSE_1H`: unchanged — already specified as never at or after the apply end time (this scenario already passes; documented here for completeness).
  - `APPLY_OPEN`: never requested once the apply end time has passed, when known.
  - `RESULT_DAY`: never requested after the end of the calendar day, in the fan's time zone, of the lottery result time.
- `scan-due-reminders` quiet hours: the pre-quiet fallback for a deadline stage moves from 22:00 (the start of the quiet window) to 21:00 (one hour before it), so the fallback's own due time always falls outside quiet hours — the reminder becomes due at 21:00 rather than firing at the window's first instant. The implementation keeps a defensive skip for the case where even 21:00 would not be strictly before the apply end time, but this cannot currently occur for either close stage given their fixed 1h/24h anchor-to-deadline offsets, so it is not asserted as spec-level (tested) behavior here — it is a safety net documented in the code, not a scenario.
- `get-reminded-of-ticket-sale-milestones` (story): update the "No reminder at night" requirement's wording to match (at 21:00, not before 22:00) and remove the resolved `Known defect: liverty-music/backend#472` note.

## Capabilities

### New Capabilities

- (none)

### Modified Capabilities

- `components/usecase/sales-phase/scan-due-reminders`: the "A stage is requested once its due time has passed" requirement gains explicit expiry rules for `APPLY_OPEN` and `RESULT_DAY`; the "Quiet hours" requirement's pre-quiet fallback moves from 22:00 to 21:00 (the reminder becomes due at 21:00, not before it); the resolved `Known defect` note is removed.
- `stories/get-reminded-of-ticket-sale-milestones`: the "No reminder at night" requirement's wording changes from "before 22:00" to "at 21:00"; the resolved `Known defect` note is removed.
- Relies on (unchanged): `components/entity/sales-phase` (attributes `apply_end_at`, `lottery_result_at`, `discovered_at` already exist and are unchanged) and `components/entity/sales-phase-reminder/list-sent-stages` (unchanged — this fix only tightens when `ScanDueReminders` decides a stage is still eligible, not how sent stages are read).

## Impact

- **Code**: `backend/internal/usecase/sales_reminder_uc.go` (`scheduledFireTime` gains an expiry return value; `processPhase` gates on it; the pre-quiet fallback hour changes from `quietStartHour` to `quietStartHour - 1`). No proto, API, or DB schema changes.
- **Tests**: table tests for `scheduledFireTime`'s new expiry values and the shifted pre-quiet hour; `ScanDueReminders`-level tests for an expired phase (no stage requested) and a not-yet-expired phase (still requested).
