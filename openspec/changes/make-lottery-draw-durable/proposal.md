## Why

The lottery draw charges before it records. `LotteryEntryUseCase.RunDraw` draws in a fresh random order, captures every winner's card authorization and releases every loser's, and only then records the outcome in one step. If the process stops between the first capture and that record, the next run draws again in a new random order. A fan who was already charged can then lose, and their release fails because the card authorization is already captured: the fan is charged without tickets. Issuance after the draw is recovered by a 1-minute sweeper, a failed release is only logged and never retried, a payment provider outage during the draw turns every winner into a loser, and a losing fan is never told the result. This change records the outcome first, charges each winner and releases each loser as durable workflows on the runtime of `introduce-durable-workflows`, and tells every fan the result. It is written on the model of `remodel-ticket-sales` (an Order exists Pending from the entry on, and issuance makes it Paid) and is applied after that change.

## What Changes

- `LotteryEntryUseCase.Draw` replaces `RunDraw`. It computes the outcome of each TicketStock of the sale's events once and records Won and Lost for the whole sale in one step, with the Lost entries' Orders Void, before any card is charged or released. A stopped draw resumes with the same outcome. `PersistDrawOutcome` changes nothing when the sale is already drawn.
- **BREAKING** (for readers of the state): Won means the draw allocated the tickets; the card is charged afterwards, so a Won entry's Order is Pending until it is Paid.
- `OrderUseCase.Issue` runs once for each Won entry. It reads everything it needs first, then captures the card authorization, makes the Pending Order Paid with its Tickets and its Settlement, and announces the Order as paid. A capture that fails because the payment provider cannot be reached is tried again for up to 24 hours. A card authorization that can no longer be charged makes the entry Lost and its Order Void (`LotteryEntry.RevertWin`). It replaces `IssueFromCapturedWin` and the `IssueDueWins` sweeper.
- `LotteryEntryUseCase.ReleaseCardAuthorization` releases the card authorization of each Lost entry, trying again for up to 24 hours. Every Lost entry is released by its own workflow, so no release is left behind; one that cannot finish is reported to an admin.
- Every fan is told the result: a winner by the confirmation email and push, which now say the entry won; a loser by a new loss email and `lottery_loss` push (`NotificationUseCase.SendLotteryLoss`, `LotteryEntry.SendLossEmail`).
- `DrawDueSales` runs on the workflow runtime's schedule every minute and starts `Draw` once per sale.
- `OrderUseCase.FulfillPayment` acknowledges a lottery capture without effect: `Issue` already issued and announced it.
- `CardAuthorization.Capture` and `Release` never return a failure an earlier call received, so a payment provider error does not repeat after the provider recovers.

## Capabilities

### New Capabilities

- `components/entity/lottery-entry/revert-win`: makes a Won entry whose Order is Pending Lost and its Order Void.
- `components/entity/lottery-entry/send-loss-email`: emails a Lost entry's fan once.
- `components/usecase/lottery-entry/draw`: draws one closed sale without charging.
- `components/usecase/lottery-entry/release-card-authorization`: releases a Lost entry's card authorization.
- `components/usecase/order/issue`: charges a Won entry and makes its Order Paid with its Tickets and Settlement.
- `components/usecase/notification/send-lottery-loss`: tells a losing fan by email and push.

### Modified Capabilities

- `components/entity/card-authorization/capture`, `release`: a failure an earlier call received is never returned again.
- `components/entity/lottery-entry/persist-draw-outcome`: admits entries in draw order against the stock's remaining count when recording, and changes nothing for entries already decided.
- `components/entity/lottery-entry` (Purpose, edited in the main spec): the state diagram gains Won to Lost; Won means the draw allocated the tickets; new attribute loss email send time.
- `components/entity/notification` (Purpose, edited in the main spec): new type lottery_loss.
- `components/entity/order/list-lottery-entry-ids-awaiting-issuance`: removed; its only caller goes.
- `components/usecase/lottery-entry/run-draw`: removed, replaced by `draw`.
- `components/usecase/lottery-entry/draw-due-sales`: starts `Draw` once per sale.
- `components/usecase/order/issue-from-captured-win`, `issue-due-wins`: removed, replaced by `issue`.
- `components/usecase/order/fulfill-payment`: a lottery capture is acknowledged without effect.
- `components/usecase/notification/send-order-confirmation`: says the entry won for a lottery Order.
- `components/usecase/notification/deliver`: runs for `SendLotteryLoss` too.
- `stories/win-tickets-in-a-lottery` (Purpose edited in the main spec, and requirements): no time bound; the fan is told the result; new requirements for a draw that stops midway and for a winner whose card can no longer be charged.

Unchanged and why: `components/entity/order/issue` already makes the Pending Order Paid with its Tickets and Settlement together and fails with AlreadyExists for an Order already Paid (`remodel-ticket-sales`); `components/entity/lottery-entry/list-undrawn-for-ticket-type` and `run-lottery-draw` keep their contracts; `components/entity/ticket-sale/list-due-for-draw` already returns a sale 1 minute after its end.

## Impact

- **Applied after `remodel-ticket-sales`**: the deltas of `run-draw`, `issue-from-captured-win`, `persist-draw-outcome` and `stories/win-tickets-in-a-lottery` are written against the main specs as that change leaves them. This change is validated and archived after it.
- **backend**: `Draw`, `ReleaseCardAuthorization`, `Issue` and `SendLotteryLoss`; the `payment` queue and the `draw-due-sales` schedule in `workflow-worker`; a migration for `lottery_entries.loss_email_send_at`; removal of `RunDraw`, `IssueFromCapturedWin`, `IssueDueWins`, `ListLotteryEntryIDsAwaitingIssuance` and the two sweeper goroutines.
- **frontend**: none; the push opens existing screens.
- **Depends on**: `introduce-durable-workflows` (archived 2026-10-28) released, and `remodel-ticket-sales` released.
- **Not in this change**: the first-come checkout (`unify-order-issuance`), the other sweepers, and promotion of a loser (繰上げ).
