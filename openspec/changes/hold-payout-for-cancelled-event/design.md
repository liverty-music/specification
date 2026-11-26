## Context

See proposal.md for the motivation. The current state, read on backend `main` after pull request #917:

- `ReleaseDueSettlements` takes every Held Settlement (`ListHeld`, `WHERE status = 1`, no join). For each one it reads the Order, checks the time gate (`entity.IsReleaseEligible` over `GetEventStartTime`), then the payout account, resolves the charge, creates one Stripe Transfer per split and calls `MarkReleased`. It never reads the Event's publish state.
- Event states are DRAFT, PUBLISHED and CANCELLED. CANCELLED is terminal. `Series.Cancel` has no time limit, so an Event can be cancelled before, during or long after its date.
- `OrderUseCase.Refund` handles a Held Settlement by reversing nothing and recording it Reversed, and a Released one by creating a transfer reversal per paid split first. `Refund all` on the admin console calls it once per Paid Order of a CANCELLED Event.
- `Concert.Delete` refuses an Event with a Settlement that is not Reversed.

## Goals / Non-Goals

**Goals:**

- No payout call for an Order of an Event that a run reads as CANCELLED.
- Add no state, no stored data and no manual step.

**Non-Goals:**

- Automatic refund. The owner kept `Refund all` manual.
- An alert or a screen that tells an admin a cancelled Event still has Paid Orders. Today the admin finds it on the Artist concerts screen. Adding a signal is a separate decision.
- Cancellation after the payout. A refund already claws a Released Settlement back (`usecase/order/refund` "Payout clawed back"); the platform fee was never paid out and any negative balance on the Organizer's payout account is the platform's, as `entity/settlement` states.
- Closing the existing race between a refund and a running sweep, or recovering a payout that was made but not recorded (see Risks).

## Decisions

### 1. The Settlement stays Held; the release rule refuses it

The Event's publish state becomes an input of release eligibility. `entity.IsReleaseEligible` returns false for a CANCELLED Event. Held already means what is true of a withheld Settlement: its money has not been paid out and is with the platform (the exception is the unrecorded payout under Risks). The refund then moves it to Reversed through the existing path.

Alternatives rejected:

- **A new status (Withheld, Frozen).** It repeats a fact the Event already holds, and needs a proto enum value, a migration, a writer triggered by `Event.Cancelled` and changes to `MarkReleased`, `CommitRefund`, resale issuance and `Concert.Delete`. Until the writer runs, the sweep would still have to read the Event.
- **Make the Settlement Reversed at cancellation**, in `Series.CancelEvents` or in a consumer of `Event.Cancelled`. Reversed would then be recorded while the fan's money is still held, `OrderUseCase.Refund` treats a Reversed Settlement as one with nothing left to claw back, and a consumer leaves a gap between the cancellation and the write.
- **Filter in `Settlement.ListHeld`** by joining the Event. It is a one-line change, but the work list is read once at the start of a run, so a cancellation during a long run would be missed for every later Settlement. It also hides a money rule in a query and makes "every Held Settlement" untrue.

### 2. Read the publish state per Settlement with `Event.Get`

The usecase receives the existing `entity.EventRepository` and calls `Get` for each Held Settlement, next to the `GetEventStartTime` call it already makes, before any Stripe call. A CANCELLED Event is logged at Info level and skipped, like the other withheld payouts, so no payout account is refreshed for it. The release time stays the instant `releaseOne` takes before this read, as today, so a cancellation stored before a Settlement's release time was always seen by the run that released it; the production check of the Migration Plan relies on this.

Alternatives rejected:

- **Return the publish state from `Event.GetEventStartTime`.** `globalize-venues` is rewriting that requirement; two changes would modify the same text, and the operation also serves ticket sales.
- **Replace `GetEventStartTime` with `Event.Get`.** One query instead of two, but the `Event.Get` spec does not promise the Venue's time zone that the start instant needs, and promising it would again overlap `globalize-venues`. The extra query costs nothing at this scale.

### 3. No lock between the check and the payout

This is a check-then-act write: read "not CANCELLED", then pay. It locks no rows. `Series.CancelEvents` can commit between the read and `CreatePayout`, a window of the payout account refresh, the charge lookup and the transfer, a few seconds. In that case the run pays and the Settlement becomes Released, which is the same outcome as a cancellation made a few seconds after the payout: `Refund all` reverses the transfer. The spec states this limit ("Cancelled after the run read the event").

Alternatives rejected:

- **Hold a lock on the event row (`SELECT ... FOR SHARE`) across the Stripe calls.** It would make `CancelEvents` wait on the payment provider and keeps a database transaction open over a network call, to move a payout and a cancellation seconds apart from "paid then clawed back" to "not paid".
- **A claim state (Releasing) taken before the transfer.** This is the right tool for the refund race under Risks, but it needs a new status, a migration and recovery of stuck claims; it belongs to that fix.

### 4. Refunds, existing data and deletion need no change

A Held Settlement of a cancelled Event leaves the work list when its Order is refunded (`Refund all`, or a dispute). Until then it is read on every run and withheld, including a Settlement created for an Order that became Paid around the cancellation. The rule reads the current state, so it also covers Events cancelled before this ships.

### 5. Overlap with `globalize-venues`

- Backend: release 2 (pull request #917, merged 2026-11-26 10:11 UTC, not yet released when this was written; its task 14.7 is open) changes the same release gate: `GetEventStartTime` now returns the local date, start time and Venue zone, and the sweep computes the instant. This change branches from `main` with #917 and is merged only after release 2 has been released, so release 2 ships and is verified without a second change to the payout path.
- Specs: `globalize-venues` modifies `components/entity/event` and `entity/event/get-event-start-time`, and touches none of the three specs this change modifies. The two can be archived in either order.
- Cancellation: it does not change `Series.Cancel`, `Series.CancelEvents` or publish states.
- Its task 14.4 tests Settlement eligibility with a Venue in `Europe/London`; those tests keep their expectations, with an Event that is not cancelled.

## Risks / Trade-offs

- [A fan is not refunded because nobody runs `Refund all`] → The money now stays with the platform instead of reaching the Organizer, but nothing reminds the admin. Accepted for the pilot, where one Organizer is in direct contact.
- [A mistaken cancellation blocks the payout for good, because CANCELLED is terminal] → The fans were already told of the cancellation and the refund, so refunding is the consistent outcome. Paying the Organizer anyway would be a manual transfer outside the product.
- [A cancellation seconds before a payout does not stop it] → Decision 3; `Refund all` claws it back.
- [A payout made but not recorded, then a cancellation] → `CreatePayout` and `MarkReleased` are separate steps. If the transfer succeeds and recording fails (database unavailable, worker stopped), today the next run repeats `CreatePayout` under the same idempotency key, gets the same transfer and records Released. If the Event is cancelled before that happens, the new rule withholds the Settlement: it stays Held, a refund reverses nothing, and the Organizer keeps the transfer. It needs a failure between two consecutive calls and a cancellation of an Event that started more than 7 days ago before a run succeeds, normally within 5 minutes. Accepted: the admin reverses the transfer in the payment provider's dashboard; the worker logs `Stripe Transfer created` with the settlement id, followed by the release failure. Alternatives rejected here: calling `CreatePayout` again for a cancelled Event would make a new payout when none exists (the provider keeps idempotency keys only 24 hours); looking up the provider's transfers needs a new entity operation and a provider read for every withheld Settlement. The claim state of Decision 3 is where this is fixed, with the race below. The MVP has one split per Settlement, so a partly paid multi-split Settlement cannot occur today.
- [Existing race: a refund committed while a sweep runs] → `ListHeld` is a snapshot, and a Settlement made Reversed by a refund after the snapshot can still be paid; `MarkReleased` then fails and the run skips it, leaving a transfer nobody reverses. A refund that reads Held just before `MarkReleased` has the same result. This change closes it for 中止 refunds except within the window of Decision 3, because the run reads the cancellation before paying. A dispute refund of an Event that is not cancelled stays exposed. It exists today and is left to a separate fix.
- [A cancelled Event's Held Settlements are read every 5 minutes until refunded] → Two reads each; negligible.

## Migration Plan

1. Wait until `globalize-venues` backend release 2 is released.
2. Merge the backend pull request and cut a release. No migration, no configuration and no proto release.
3. Verify read-only in production that the workflow worker runs the new release and that no Settlement released since then belongs to an Event that was already CANCELLED at its release time. Released Settlements of Events cancelled after the payout, and those released before the rollout, are expected and are clawed back by their refunds.

Rollback is the previous image; no data was written by this change. A rollback releases due Settlements of cancelled Events again, so run `Refund all` for them first.
