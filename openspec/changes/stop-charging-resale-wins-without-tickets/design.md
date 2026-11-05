## Context

See proposal.md, "Why". The resale path of the `issue` workflow (`issueResaleEntry`, `internal/usecase/order_resale_workflow.go`) runs these steps:

1. `read`: the plan.
2. `capture`: checks only that the clock is before the start time.
3. `issueCaptured`: reads the captured payment, then runs `issue`. The resale branch of `issue` is `sellResaleListings` in `issuance_repo.go`, which runs under the ticket stock lock.

When `issue` finds a listing that is not Listed, it fails with FailedPrecondition. Nothing is retried after that, and the Order stays Pending with no Settlement.

`OrderUseCase.Refund` (`cancellation` or `dispute`) commits through `RefundRepository.CommitRefund`. It cancels the Order's Listed listings and voids its Tickets, and it locks the Order's ticket rows.

## Goals / Non-Goals

**Goals:**
- A Won entry is never charged for a concert that is no longer PUBLISHED at the time of the charge.
- A Won entry whose allocated listing was cancelled after the charge ends with the whole charge refunded.

**Non-Goals:**
- Refusing or delaying an Order's refund while a listing of it is allocated. A dispute cannot be refused, and D2 covers the cancellation case.
- Unwinding a resale after its tickets were issued, as Ticketmaster does on a cancellation. Terms of Service article 7 keeps today's rule: the winner's own Paid Order is refunded, and the reselling fan keeps the resale refund.
- Any change on the fan screens. The entries screen shows 落選 for every lost reason.

## Decisions

### D1: Check the event before the capture, in the same step

The `capture` step first reads whether the event is still PUBLISHED, with the same read the draw uses (`EventPublishStatePort.IsEventPublished`). When the event is not PUBLISHED, the step records "cancelled" instead of capturing. The workflow then reverts the win with "concert cancelled" in its own step, as it already does for "card could not be charged". The release and the ended email follow from the announcement.

Keeping the check inside the capture step means a recovered workflow does not check again after a capture that already happened.

- **Rejected: a separate step before the capture.** A crash between the check and the capture would replay only the capture, which is the same behaviour with one more recorded step.

The check and the capture are not atomic: a concert cancelled in the seconds between them is still charged. The outcome depends on what happens next:

- If an admin then refunds the reselling fan's Order, D2 catches it.
- If not, the winner holds Paid tickets of a cancelled concert. The cancellation refund of their own Order covers that, as for any purchase. This is accepted.

### D2: Refund the charge when the sell finds a Cancelled listing

`sellResaleListings` returns a distinct error, `entity.ErrResaleListingCancelled`, when a listing allocated to the entry is Cancelled. Other states keep today's FailedPrecondition.

On that error, `issueResaleEntry` runs two more steps:

1. **`refund cancelled win`:** refunds the whole charge with `Order.CreateRefund` for the Order's own refund. The idempotency key `order-refund:<orderID>` makes a replay refund once. The charge is resolved from the captured payment's provider payment ID, which `issueCaptured` already read. Unavailable is retried for up to 24 hours, after which an admin is told. The entry stays Won meanwhile.
2. **`revert win`:** runs `RevertWin(entry, "listing cancelled")`.

**The race is serialized by ticket row locks.** `CommitRefund` locks the reselling fan's Order's ticket rows. `sellResaleListings` updates the same rows when it voids the listed Tickets. Whichever transaction commits second sees the result of the first:

- **The refund commits first:** the listing is Cancelled, so the sell gets `ErrResaleListingCancelled`.
- **The sell commits first:** the listing is Sold and its Ticket Voided. The refund then reaches only unresold tickets (`unresoldAmount`), and the listing fan's resale refund stands.

The implementation verifies that `sellResaleListings` takes these row locks; where it does not, it locks the listed ticket rows with `FOR UPDATE` before checking the listings.

- **Rejected: refusing the refund** (the first idea in backend#778). It cannot cover a dispute, and an admin's cancellation refund would have to be retried by hand.

### D3: A new lost reason, LISTING_CANCELLED

What follows a Lost entry is decided from its lost reason alone: the release in `StartResaleEntryWorkflow`, and the text in `SendResaleEntryEnded`. A charged-and-refunded win needs both to differ from an uncharged loss:

- no release, since the release would fail with FailedPrecondition and alert an admin every time;
- an email saying the charge is refunded, not "nothing was charged".

A new reason keeps that decision in the data, the same way "payment not completed before the show" skips the release today.

- **Rejected: reusing "concert cancelled" / "no ticket left"** and branching on the Order's state instead. This needs a refunded-but-never-Paid Order state and a second branch in two places.

What the new reason needs:

- **Proto:** `RESALE_ENTRY_LOST_REASON_LISTING_CANCELLED = 5` in `resale_entry.proto`.
- **DB:** the `chk_resale_entries_lost_reason` check widens from 1..4 to 1..5, and the column comment changes.
- **Entity:** the `ResaleEntryLostReason` constant, and its pb mapping.

### D4: RevertWin keeps listings that are not Listed

`RevertWin` frees the listings allocated to the entry today by clearing `resale_entry_id`. With "listing cancelled", one of them is Cancelled. Clearing its `resale_entry_id` changes nothing a fan sees, because only a Listed listing is free for a draw. The spec still says "still Listed", so the record shows that a cancelled listing is not offered again.

- **Order state:** the Order is made Void. It never became Paid, so it has no Settlement to reverse, and the refund is recorded at the payment provider under the Order's own refund key. The Organizer is paid for that seat by neither Order, which is right: the reselling fan's Order was refunded too.

## Risks / Trade-offs

- **[A concert cancelled between D1's check and the capture]** → The winner is charged and, unless D2 applies, issued tickets. The cancellation refund of their own Order covers it, as for any Paid Order.
- **[The refund in D2 fails for 24 hours]** → The entry stays Won with a captured charge and no tickets, and an admin is told. The fan sees a charge until the admin refunds it.
- **[The fan sees a charge and then a refund]** → The ended email says the charge is refunded. How long the refund takes to appear depends on the card issuer.

## Migration Plan

1. specification: proto PR adding the enum value, then a Release, then BSR generation.
2. backend:
   - the migration widening the lost reason check;
   - code and tests, built against the new generated types;
   - merge, then cut the release. The migration applies at merge. It only widens a check, so the running image is unaffected.
3. No frontend release. An unknown lost reason maps to the same 落選 state.
