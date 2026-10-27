## Why

The lottery draw charges before it records. `LotteryEntryUseCase.RunDraw` draws in a fresh random order, captures every winner and releases every loser, and only then records the outcome in one transaction. If the process stops between the first capture and that record, the next run draws again in a new random order. A fan who was already charged can then lose, and their release fails because the card authorization is already captured: the fan is charged without tickets. The steps after the draw are recovered by a 1-minute sweeper (issuance) or not at all (a failed release is only logged), and a payment provider outage during the draw turns every winner into a loser. A losing fan is never told the result. This change records the outcome first, runs the charge and the release of each entry as a durable workflow on the runtime of `introduce-durable-workflows`, and tells every fan the result.

## What Changes

- `LotteryEntryUseCase.Draw` replaces `RunDraw`. It computes the outcome once and records Won and Lost for the whole sale in one step, before any card is charged or released. A stopped draw resumes with the same outcome. `PersistDrawOutcome` changes nothing when the sale is already drawn.
- A Won entry means the draw allocated its tickets. It is charged afterwards. **BREAKING** (for readers of the state): Won no longer implies a captured card authorization.
- `OrderUseCase.Issue` runs once for each Won entry. It reads everything first, then captures, issues the Order, its Tickets and its Settlement, and announces the Order as paid. A capture that fails because the payment provider cannot be reached is tried again for up to 24 hours. A card authorization that can no longer be charged makes the entry Lost (`LotteryEntry.RevertWin`). It replaces `IssueFromCapturedWin` and the `IssueDueWins` sweeper.
- `LotteryEntryUseCase.ReleaseCardAuthorization` releases the card authorization of each Lost entry, trying again for up to 24 hours.
- Every fan is told the result: a winner by the confirmation email and push, which now say the entry won; a loser by a new loss email and `lottery_loss` push (`NotificationUseCase.SendLotteryLoss`, `LotteryEntry.SendLossEmail`). The story no longer promises a time: the draw runs after the window closes and each fan is told.
- `DrawDueSales` runs on the workflow runtime's schedule every minute and draws each sale once.
- `OrderUseCase.FulfillPayment` no longer issues or announces for a won lottery entry: `Issue` already did.

## Capabilities

### New Capabilities

- `components/entity/lottery-entry/revert-win`: makes a Won entry with no Order Lost.
- `components/entity/lottery-entry/send-loss-email`: emails a Lost entry's fan once.
- `components/usecase/lottery-entry/draw`: draws one closed sale without charging.
- `components/usecase/lottery-entry/release-card-authorization`: releases a Lost entry's card authorization.
- `components/usecase/order/issue`: charges a Won entry and issues its Order, Tickets and Settlement.
- `components/usecase/notification/send-lottery-loss`: tells a losing fan by email and push.

### Modified Capabilities

- `components/entity/lottery-entry` (Purpose): the state diagram gains Won to Lost; Won means the draw allocated the tickets; new attribute loss email send time.
- `components/entity/lottery-entry/persist-draw-outcome`: changes nothing for a sale already drawn.
- `components/entity/notification` (Purpose): new type lottery_loss.
- `components/entity/ticket-sale`: the result time no longer states a draw time bound.
- `components/entity/order/list-lottery-entry-ids-awaiting-issuance`: removed; its only caller goes.
- `components/usecase/lottery-entry/run-draw`: removed, replaced by `draw`.
- `components/usecase/lottery-entry/draw-due-sales`: runs `Draw` once per sale.
- `components/usecase/order/issue-from-captured-win`, `issue-due-wins`: removed, replaced by `issue`.
- `components/usecase/order/fulfill-payment`: a lottery charge is acknowledged without effect.
- `components/usecase/notification/send-order-confirmation`: says the entry won for a lottery Order.
- `components/usecase/notification/deliver`: runs for `SendLotteryLoss` too.
- `stories/win-tickets-in-a-lottery`: no time bound; the fan is told the result; new requirements for a draw that stops midway and for a winner whose card can no longer be charged.

Unchanged and why: `components/entity/order/issue` already stores the Order, its Tickets and its Settlement together and fails with AlreadyExists for a second Order of the same source; `components/entity/card-authorization/capture` and `release` already succeed again for a repeated call; `components/entity/lottery-entry/list-undrawn-for-ticket-type` and `run-lottery-draw` keep their contracts; `components/entity/ticket-sale/list-due-for-draw` already returns a sale 1 minute after its end.

## Impact

- **backend**: `Draw`, `ReleaseCardAuthorization`, `Issue` and `SendLotteryLoss`; the `payment` queue and the `draw-due-sales` schedule in `workflow-worker`; a migration for `lottery_entries.loss_email_send_at`; removal of `RunDraw`, `IssueFromCapturedWin`, `IssueDueWins`, `ListLotteryEntryIDsAwaitingIssuance` and the two sweeper goroutines.
- **frontend**: none; the push opens existing screens.
- **Depends on**: `introduce-durable-workflows` released (worker, `Flow`, `Workflows`, the alert).
- **Not in this change**: the first-come checkout (`unify-order-issuance`), the other sweepers, and promotion of a loser (繰上げ).
