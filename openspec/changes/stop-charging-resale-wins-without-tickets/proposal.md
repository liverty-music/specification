## Why

A Won resale entry is charged before its tickets are issued, and two things can go wrong between those steps ([backend#778](https://github.com/liverty-music/backend/issues/778)):

- **The concert was cancelled.** The charge checks only that the show has not started, so a Won entry is still charged and issued for a concert that has since been cancelled.
- **The allocated listing was cancelled.** An admin refunds the reselling fan's original Order, either for a cancellation or because of a chargeback (dispute). That cancels the listing. The issue step then fails, and the winning fan is charged with no ticket.

A dispute cannot be refused: the card network has already taken the money back. So the issue path itself has to stop charging, or give the charge back.

## What Changes

- Before charging a Won entry, `OrderUseCase.Issue` checks that its event is still PUBLISHED. When it is not, Issue charges nothing and makes the entry Lost with "concert cancelled" through `ResaleEntry.RevertWin`. The card authorization is then released, and the fan is told, from that announcement.
- When the issue step after a charge finds a listing allocated to the entry Cancelled, Issue refunds the whole charge with `Order.CreateRefund`. It then makes the entry Lost with a new lost reason, "listing cancelled", through `ResaleEntry.RevertWin`. No card authorization is released for it, because it was charged and refunded.
- `ResaleEntry.RevertWin` accepts the lost reasons "concert cancelled" and "listing cancelled" besides the two it accepts today.
- `SendResaleEntryEnded` tells a fan whose entry lost with "listing cancelled" that the win was cancelled and the charge is refunded.
- A new value of the proto enum `ResaleEntryLostReason`: `LISTING_CANCELLED`.
- Refunds of the reselling fan's Order stay as they are. They are not refused while a listing of it is allocated.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/usecase/order/issue`: "Issue a won resale entry" checks the event before charging, and gives back a charge whose listing was cancelled.
- `components/entity/resale-entry/revert-win`: accepts the lost reasons "concert cancelled" and "listing cancelled". The second reverts a win that was charged and refunded.
- `components/entity/resale-entry` (Purpose): the lost reason attribute gains "listing cancelled". This is edited directly in the main spec.
- `components/usecase/order/release-card-authorization`: runs for a win reverted with "concert cancelled", and not for one reverted with "listing cancelled".
- `components/usecase/notification/send-resale-entry-ended`: the message for "listing cancelled".
- Unchanged and relied on: `components/entity/order/create-refund`, whose own-refund purpose refunds the whole charge once per Order, and `components/entity/resale-listing`, whose Cancelled state is what an Order's refund sets.

## Impact

- **specification:** `proto/liverty_music/entity/v1/resale_entry.proto` gains `RESALE_ENTRY_LOST_REASON_LISTING_CANCELLED`, which needs a proto PR and a Release.
- **backend:**
  - the resale path of `issueResaleEntry` (`internal/usecase/order_resale_workflow.go`);
  - the `RevertWin` repository method;
  - the release decision in `StartResaleEntryWorkflow`;
  - the ended email and push texts;
  - the pb mapping of the lost reason;
  - a migration widening the `resale_entries.lost_reason` check.
- **frontend:** none. The entries screen shows 落選 for any lost reason, and an unknown enum value maps to the same state.
- **Money:** a refunded charge goes back through the payment provider. No Settlement is recorded for the reverted Order, so the Organizer is still paid at most once per seat.
