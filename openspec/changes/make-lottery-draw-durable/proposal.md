## Why

The lottery draw charges before it records. `LotteryEntryUseCase.RunDraw` draws in a fresh random order, captures every winner's card authorization and releases every loser's, and only then records the outcome in one step. If the process stops between the first capture and that record, the next run draws again in a new random order. A fan who was already charged can then lose, and their release fails because the card authorization is already captured: the fan is charged without tickets. Issuance after the draw is recovered by a 1-minute sweeper, a failed release is only logged and never retried, a payment provider outage during the draw turns every winner into a loser, and a losing fan is never told the result. This change records the outcome first, charges each winner and releases each loser as durable workflows on the runtime of `introduce-durable-workflows`, and tells every fan the result. It is written on the model of `remodel-ticket-sales` (an Order exists Pending from the entry on, and issuance makes it Paid) and on the announcements of `publish-events-through-outbox` (an entity operation announces its change in its own transaction), and is applied after both.

## What Changes

- `LotteryEntryUseCase.Draw` replaces `RunDraw`. It computes the outcome of each TicketStock of the sale's events once and records Won and Lost for the whole sale in one step, with the Lost entries' Orders Void, before any card is charged or released. A stopped draw resumes with the same outcome. `PersistDrawOutcome` changes nothing when the sale is already drawn. Each entry it records is announced with the outcome, and the consumer of that announcement starts the charge of a Won entry and the release of a Lost one; `Draw` starts no workflow per entry.
- **BREAKING** (for readers of the state): Won means the draw allocated the tickets; the card is charged afterwards, so a Won entry's Order is Pending until it is Paid.
- `OrderUseCase.Issue` runs once for each Won entry. It reads everything it needs first, then captures the card authorization, and makes the Pending Order Paid with its Tickets and its Settlement through `Order.Issue`, which announces it as paid. A capture that fails because the payment provider cannot be reached is tried again for up to 24 hours. A card authorization that can no longer be charged makes the entry Lost with the lost reason "card could not be charged" and its Order Void (`LotteryEntry.RevertWin`, which announces the entry). It replaces `IssueFromCapturedWin` and the `IssueDueWins` sweeper.
- `OrderUseCase.ReleaseCardAuthorization` releases the card authorization of each Lost entry's Order, which is Void, trying again for up to 24 hours. Every Lost entry is released by its own workflow, so no release is left behind; one that cannot finish is reported to an admin.
- Every fan is told the result: a winner by the confirmation email and push, which now say the entry won; a loser by a new loss email and `lottery_loss` push (`NotificationUseCase.SendLotteryLoss`, `LotteryEntry.SendLossEmail`).
- `DrawDueSales` runs on the workflow runtime's schedule every minute and starts `Draw` once per sale.
- `OrderUseCase.FulfillPayment` acknowledges a lottery capture without effect: `Issue` already issued it, and `Order.Issue` announced it.
- `CardAuthorization.Capture` and `Release` never return a failure an earlier call received, so a payment provider error does not repeat after the provider recovers.

## Capabilities

### New Capabilities

- `components/entity/lottery-entry/revert-win`: makes a Won entry whose Order is Pending Lost, with the lost reason "card could not be charged", and its Order Void, and announces the entry.
- `components/entity/lottery-entry/send-loss-email`: emails a Lost entry's fan once.
- `components/usecase/lottery-entry/draw`: draws one closed sale without charging.
- `components/usecase/order/release-card-authorization`: releases a Void Order's card authorization (a Lost lottery entry's here; `resell-tickets-by-lottery` reuses it).
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
- `components/infrastructure/backend/process/trace-propagation`: a scheduled workflow records no trace for a run that finds nothing, and each workflow it starts is its own trace (design "Traces: a schedule run that finds no sale records nothing"). The capability is created by `fix-trace-propagation`.
- `components/usecase/order/issue-from-captured-win`, `issue-due-wins`: removed, replaced by `issue`.
- `components/usecase/order/fulfill-payment`: a lottery capture is acknowledged without effect.
- `components/usecase/notification/send-order-confirmation`: says the entry won for a lottery Order.
- `components/usecase/notification/deliver`: runs for `SendLotteryLoss` too.
- `stories/win-tickets-in-a-lottery` (Purpose edited in the main spec, and requirements): no time bound; the fan is told the result; new requirements for a draw that stops midway and for a winner whose card can no longer be charged.

Unchanged and why: `components/entity/order/issue` already makes the Pending Order Paid with its Tickets and Settlement together and fails with AlreadyExists for an Order already Paid (`remodel-ticket-sales`); `components/entity/lottery-entry/list-entered-by-ticket-sale-and-ticket-stock` and `run-lottery-draw` keep their contracts; `components/entity/ticket-sale/list-due-for-draw` already returns a sale 1 minute after its end.

## Impact

- **Applied after `remodel-ticket-sales`**: the deltas of `run-draw`, `issue-from-captured-win`, `persist-draw-outcome` and `stories/win-tickets-in-a-lottery` are written against the main specs as that change leaves them. This change is validated and archived after it.
- **backend**: `Draw`, `ReleaseCardAuthorization`, `Issue` and `SendLotteryLoss`; the `payment` queue and the `draw-due-sales` schedule in `workflow-worker`; a migration for `lottery_entries.loss_email_send_at`; removal of `RunDraw`, `IssueFromCapturedWin`, `IssueDueWins`, `ListLotteryEntryIDsAwaitingIssuance` and the two sweeper goroutines.
- **frontend**: none; the push opens existing screens.
- **Applied after `publish-events-through-outbox`**: the deltas of `persist-draw-outcome`, `fulfill-payment` and `deliver` are written against the main specs as that change leaves them (the lost reason, "Each completed charge ends in an issued Order", Deliver started by name).
- **Depends on**: `introduce-durable-workflows` (archived 2026-10-28) released, then `remodel-ticket-sales` and `publish-events-through-outbox` released, in that order.
- **Not in this change**: the first-come checkout (`unify-order-issuance`), the other sweepers, and promotion of a loser (繰上げ).
