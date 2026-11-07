## Why

A concert can be cancelled (中止) while its lottery is open, and the lottery carries on as if nothing happened. liverty-music/specification#1240 assumes the draw never runs for a cancelled Event. It does: `TicketSale.ListDueForDraw`, `LotteryEntryUseCase.Draw` and `OrderUseCase.Issue` never read the Event's state, and `AuthorizeCard` and `Confirm` accept new entries. So when the window closes, the winners' cards are charged and Tickets are issued for a concert that will not happen, and the losers are told they were not drawn. Official resale and checkouts already refuse a cancelled concert; lottery entries are the one source that does not.

Until the window closes (at most 14 days), each entry also keeps its card authorization open and, as a Pending Order, blocks the Event's deletion (`Concert.DeleteAndSuppress`).

The pilot sells first come, first served, so no fan is affected today (liverty-music/specification#1074). The lottery must stay usable at any time, so this is fixed now rather than when a lottery is first run.

## What Changes

- `OrderUseCase.Issue` checks that the Event is PUBLISHED before each attempt to charge a Won lottery entry. When it is not, it charges nothing and makes the entry Lost with a new lost reason, "concert cancelled". This is the check that keeps money safe; official resale already has the same one.
- `LotteryEntryUseCase.AuthorizeCard` and `Confirm` refuse a cancelled concert. `Confirm` releases the card authorization it refuses.
- New `LotteryEntryUseCase.EndForCancelledEvent`, run for each announcement of a cancelled Event: every Entered entry of the Event becomes Lost with the lost reason "concert cancelled" and its Order Void, so the card authorization is released and the fan told within seconds of the cancellation rather than when the window closes.
- `NotificationUseCase.SendLotteryLoss` gains one wording for the new lost reason, used whether the entry was Entered or Won.

Deliberately not changed, because they add little once the above is in place:

- A Held Checkout is not released early. `Checkout.Start` and `OrderUseCase.Place` already refuse a cancelled concert, and the hold ends within 15 minutes.
- `LotteryEntryUseCase.Draw` gets no check of its own. An entry the end above missed is stopped by the check in `Issue`.
- `OrderUseCase.Issue` gets no check for a placed Checkout. `Place` checks immediately before it.
- TicketSales of a cancelled Event are not ended. The sale may name other dates, and the refusals above work per Event.

## Capabilities

### New Capabilities

- `components/entity/lottery-entry/end-entered-by-event`: makes every Entered entry of an Event Lost with the lost reason "concert cancelled" and its Order Void, and announces each.
- `components/usecase/lottery-entry/end-for-cancelled-event`: runs that operation for each Event announced as cancelled.

### Modified Capabilities

- `components/entity/lottery-entry` (Purpose): the lost reason attribute gains "concert cancelled".
- `components/entity/lottery-entry/revert-win`: takes the lost reason. Its Purpose is also edited, since a win is now reverted for two reasons.
- `components/usecase/lottery-entry/authorize-card`: refuses a cancelled concert.
- `components/usecase/lottery-entry/confirm`: refuses a cancelled concert and releases the card authorization.
- `components/usecase/order/issue`: checks the Event before charging a Won lottery entry.
- `components/usecase/order/release-card-authorization`: also runs for an entry `EndEnteredByEvent` makes Lost.
- `components/usecase/notification/send-lottery-loss`: also runs for that entry, and words the new lost reason.
- `stories/win-tickets-in-a-lottery`: a cancellation ends the lottery for that Event, and no fan is charged for it. Its usecase diagram (Purpose) gains the new usecase.
- `stories/remove-a-cancelled-concert`: an open lottery entry no longer holds up the deletion.

The usecases also rely on `Event.IsEventPublished`, `Order.Get` and `CardAuthorization.Release`, which do not change. `Series.CancelEvents` already announces each cancelled Event and does not change. `TicketSale.ListDueForDraw`, `LotteryEntry.PersistDrawOutcome` and `LotteryEntryUseCase.Draw` do not change: `PersistDrawOutcome` already leaves an entry that is no longer Entered as it is.

## Impact

- **specification**: `LOTTERY_ENTRY_LOST_REASON_CONCERT_CANCELLED` is appended to `LotteryEntryLostReason`, because an announcement carries the reason. The value is additive. The frontend does not read the lost reason, so it needs no change.
- **cloud-provisioning**: one new NACK Consumer on `CONCERT.cancelled`.
- **backend**: a migration widening `chk_lottery_entries_lost_reason`, the new entity operation, the usecase, the receiver, the checks and the wording.
- Issue: liverty-music/specification#1240.
