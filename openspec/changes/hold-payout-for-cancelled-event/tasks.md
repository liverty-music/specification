The backend pull request is merged only after backend release 2 of `globalize-venues` has been released (design Decision 5). Branch from a backend `main` that contains pull request #917.

## 1. backend: entity (components/entity/settlement; Decision 1)

- [ ] 1.1 Make `entity.IsReleaseEligible` return false for a CANCELLED Event; verify one unit test per scenario of "Release eligibility", each annotated `@spec`: "Start time unknown", "Buffer not yet elapsed", "Buffer elapsed" and "Cancelled event" (the first three exist without the annotation)

## 2. backend: usecase (components/usecase/settlement/release-due-settlements; Decisions 2 and 3)

- [ ] 2.1 Give the settlement usecase the `entity.EventRepository`, read each Settlement's Event with `Get` before any payment provider call, withhold a CANCELLED one with an Info log, keep skipping an Event that does not exist, and wire the repository in the workflow worker; verify one `@spec` unit test per scenario of "Release 7 days after the event's current start": "Before the event plus 7 days", "Event start unknown", "Start time filled in after the purchase", "Cancelled event past the buffer" (no payout account read, `CreatePayout` or `MarkReleased` call), "Cancelled after the run read the event" (the Event is cancelled after `Get` returned PUBLISHED, and the split is still paid and recorded) and "Cancelled before a failed release is recorded" (`MarkReleased` fails on the first run, and the second run, reading CANCELLED, calls neither `CreatePayout` nor `MarkReleased`)

## 3. backend: story (stories/remove-a-cancelled-concert)

- [ ] 3.1 Extend the cancelled-concert story integration test with the payout sweep over an in-memory payout provider and an Active payout account; verify "Release date passes before the refunds" (no payout, both Settlements Held) and "Refunded after the release date" (both Orders Refunded, both Settlements Reversed, no payout and no reversal), each annotated `@spec`

## 4. backend: release

- [ ] 4.1 Confirm that `globalize-venues` backend release 2 has been released (its task 14.7), then merge the backend pull request, cut the release and confirm read-only in production that the release is rolled out and the `release-due-settlements` workflow completes without a new error
- [ ] 4.2 Query read-only in production the Settlements of CANCELLED Events whose release time is after the rollout of task 4.1; expect none. For one that appears, take the time of the Event's `Cancel` call from the organizer console API logs: a cancellation before the release time is a defect, to record in this task and report to the owner; a later one is a cancellation after the payout (design Decision 3 and Non-Goals), which `Refund all` claws back. Also for each Held Settlement of a CANCELLED Event, confirm that the worker logs show no `Stripe Transfer created` with its id (design Risks, unrecorded payout)
- [ ] 4.3 Run `gh workflow run stripe-sandbox-e2e.yml` in backend and confirm the run succeeds

## 5. specification: Purpose and topic page (at archive)

- [ ] 5.1 Confirm the backend pull request of task 4.1 is merged and cite it
- [ ] 5.2 Edit the main specs directly, so they describe only shipped behavior: the `event` row of `components/entity/settlement` (its cancellation also blocks the release); the Purpose sentence and sequence diagram of `usecase/settlement/release-due-settlements` (`Event.Get`, withhold a CANCELLED Event); and the Purpose of `stories/remove-a-cancelled-concert` with the frames `Schedule_SettlementDue` and `SettlementUseCase_ReleaseDueSettlements`; verify `openspec validate --specs` passes
- [ ] 5.3 In `docs/topics/money-flow.html`, say that a cancelled Event is never paid out (the payout timing, the cancellation section and the release flow diagram), then open the page in a browser and confirm the diagram text fits its boxes
