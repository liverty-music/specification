# Tasks

## 1. Usecase (components/usecase/sales-phase/scan-due-reminders)

- [ ] 1.1 Add an expiry instant to the fire-time calculation (`APPLY_CLOSE_24H`/`APPLY_CLOSE_1H` at the apply end time; `APPLY_OPEN` at the apply end time when known, else unbounded; `RESULT_DAY` at the end of the local result day) and skip a stage once `now` reaches its expiry, even when it is otherwise due. Verify with table tests covering the new expiry values (`@spec components/usecase/sales-phase/scan-due-reminders "Application window closed before the open reminder was sent"`, `"Result day has ended"`) and a `ScanDueReminders`-level test asserting a phase whose deadline, application window and result day are all in the past publishes nothing.
- [ ] 1.2 Move the deadline-stage pre-quiet alert from 22:00 (the start of the quiet window) to 21:00 (one hour before it), and skip the stage entirely when even 21:00 is not strictly before the apply end time. Verify with updated table tests for the pre-quiet fallback (`@spec components/usecase/sales-phase/scan-due-reminders "Close before the morning"`) asserting the new 21:00 time.
- [ ] 1.3 Verify a due, not-yet-expired stage still publishes as before (regression guard for 1.1) with a `ScanDueReminders`-level test.

## 2. Story wording (stories/get-reminded-of-ticket-sale-milestones)

- [ ] 2.1 No separate implementation — the "No reminder at night" requirement's 21:00 wording is satisfied by task 1.2 and verified by the same usecase-level tests; confirm the story spec text matches the shipped behavior.
