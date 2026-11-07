## Context

See proposal.md for why. The relevant state of `backend` `main`:

- `Series.CancelEvents` records `CONCERT.cancelled` in its transaction (`series_events_repo.go`), and `send-event-cancelled` already receives it.
- `Checkout.Start`, `OrderUseCase.Place`, `ResaleEntryUseCase.Draw` and the resale path of `OrderUseCase.Issue` read `Event.IsEventPublished`. `LotteryEntryUseCase` declares that port (`lottery_entry_uc.go`) and never calls it, and neither does `issueEntry`.
- `PersistDrawOutcome` re-reads under its transaction which of the given entries are still Entered and leaves the others as they are, so a draw already tolerates an entry ended while it runs.
- An announced Lost entry already starts `ReleaseCardAuthorization` (`start-lottery-entry-workflow`) and `SendLotteryLoss` (`send-lottery-loss`). Both read `ORDER.lottery_entry_drawn`.

## Goals / Non-Goals

**Goals:** a cancelled concert never charges a lottery fan; open entries end within seconds of the cancellation; the receivers of a Lost entry are reused as they are.

**Non-Goals:** the items listed as deliberately not changed in proposal.md. A separate notification type: the existing `lottery_loss` type carries the new wording.

## Decisions

### D1. Entries end from `CONCERT.cancelled`, not in the cancellation's transaction

`CONCERT.cancelled` is stored with the cancellation, so it cannot be lost. A new receiver calls `LotteryEntryUseCase.EndForCancelledEvent`.

- **Same transaction as `CancelEvents`** was rejected. Its only advantage is that no gap exists between the cancellation and the end, and the gap is already safe: a draw in it records entries that D3 stops from being charged. It would also make a member's cancellation wait on, and fail with, every entry's announcement, and put lottery rows in `SeriesRepository`.
- **Ending entries at the draw, like resale** was rejected. Holds and the deletion block would last until the window closes, at most 14 days (`components/infrastructure/organizer/web/route/ticket-sale-editor`), and the fan would hear of it only then.
- **A DBOS workflow** was rejected for the ending. Starting one directly from `SeriesUseCase.Cancel` could be lost if the process stopped after the commit, so the announcement has to be the trigger anyway. Once it is, the work is one idempotent transaction and JetStream's redelivery (`maxDeliver: -1`) is its retry. The guard against a repeated delivery is `state = 1` (backend `AGENTS.md`, "Announcements"). The card release stays in its existing workflow, since it calls the payment provider.

### D2. `LotteryEntry.EndEnteredByEvent` lives on `LotteryEntryRepository`

In one transaction it:

1. reads the Event's TicketStocks and locks them in id order, the order `PersistDrawOutcome` and `RevertWin` use, so this transaction and a draw run one after the other;
2. updates `lottery_entries` to state 3, lost reason 3 for the entries of those stocks with `state = 1`, returning them;
3. updates their Orders to Void, guarded by `status = 4`;
4. records `ORDER.lottery_entry_drawn` for each changed entry with `pb.FromLotteryEntry`, and nothing when no row changed.

Locks, as the check-then-act rule requires: the stock rows serialize this operation with `PersistDrawOutcome`, and the `state = 1` guard decides each entry once. `LotteryEntry.Create` does not take these locks, because a `Confirm` that passes its check just before the cancellation can still make an entry just after this operation ran. That entry is not stopped here; D3 stops its charge. See Risks.

### D3. `issueEntry` checks the Event inside its capture step

The check runs at the start of the step that captures, as `order_resale_workflow.go` does:

- A step retried while the payment provider is unreachable checks again before each attempt, so a cancellation during an outage is honoured.
- A resumed run does not check again after a capture that already happened, so a charged win is never reverted.

`capture` is shared with `issueCheckout`, which keeps no such check. `issueEntry` gets its own step body, or `capture` takes a check function; the implementer chooses whichever keeps `issueCheckout`'s behaviour unchanged. An earlier attempt that failed with Unavailable may have charged the card (`components/entity/card-authorization/capture`), so on "not published" the step reads the card authorization first, as `resaleCaptureOfCancelledConcert` does. A Captured one continues as charged, and the Order becomes Paid, so `Refund all` refunds it. Otherwise the step returns "not published", and a following step calls `RevertWin` with the lost reason "concert cancelled".

`RevertWin` takes the lost reason as `ResaleEntry.RevertWin` does. `lotteryEntryRevertWinQuery` takes it as a parameter, and the existing caller passes "card could not be charged".

### D4. The new lost reason

- proto: append `LOTTERY_ENTRY_LOST_REASON_CONCERT_CANCELLED = 3`. Additive, so `buf breaking` passes.
- entity: `LotteryEntryLostReasonConcertCancelled = 3`.
- `internal/adapter/pb`: `lotteryEntryLostReasonToProto` and the list in `LotteryEntryFromAnnouncement` (`announcement.go`). Without the latter, `SendLotteryLoss`'s consumers would decode the reason as unspecified.
- schema: `chk_lottery_entries_lost_reason` allows `IN (1, 2, 3)`, and the column comment names it. A versioned migration, generated as the backend's `AGENTS.md` describes.
- analytics: `capture_failed` stays false and `result` is Lost. This adds "lottery result" events for entries that were never drawn. They can be told apart once the analytics consumer sends the reason, which is not needed now because the pilot runs no lottery.

### D5. Wording

One branch of `lotteryLossContent` per reason replaces the `cardNotCharged` boolean. The new one:

| | ja | en |
|---|---|---|
| Email subject | 【Liverty Music】公演中止のお知らせ | [Liverty Music] Your ticket lottery ended: the concert was cancelled |
| Email lead | 公演が中止になったため、チケット抽選のお申し込みは終了しました。 | The concert was cancelled, so your ticket lottery entry ended. |
| Push title | 公演が中止になりました | Concert cancelled |
| Push body | `<title>`: 抽選のお申し込みは終了しました。請求はありません。 | `<title>`: your lottery entry ended. You were not charged. |

The rest of the email (concert, entry, payment) is unchanged. The English subject follows `resale_entry_ended.go`. The push link stays `concertDeepLink`, the link the `event_cancelled` push already uses for a cancelled Event.

### D6. The receiver

Consumer `end-lottery-entries-of-cancelled-event`, stream `CONCERT`, filter `CONCERT.cancelled`, with the settings of `consumer-send-event-cancelled.yaml`, handled by a new handler that only decodes the Event and calls the usecase. It has its own durable rather than sharing `send-event-cancelled`, so a failure in one is retried without running the other. It runs in `event-consumer` beside the others.

`deliverPolicy: new` means a cancellation made before the Consumer exists is not delivered. Migration Plan covers those.

## Risks / Trade-offs

- [A draw runs in the seconds between the cancellation and the end] → The losers get the "not drawn" wording, and the winners are stopped by D3 and told the concert is cancelled. Nobody is charged, and it needs a window closing in those seconds.
- [`Confirm` passes its check just before the cancellation and makes an entry just after the end ran] → The entry stays Entered and holds the card until the window closes, at most 14 days. Its Pending Order also blocks the Event's deletion until then. Then it loses as "not drawn" or is stopped by D3. Nothing is charged. Accepted: locking this out would add a lock to `Create` for a race of milliseconds.
- [Capture runs in the instant after D3's check and the cancellation lands between them] → The Order becomes Paid on a cancelled Event, possibly after `send-event-cancelled` listed the Orders, so the fan gets no cancellation notice. `Refund all` still refunds it. The same race exists for resale today. Accepted.
- [A placed Checkout's capture is retried through a payment provider outage, and the concert is cancelled during it] → `Place` has already checked, and `issueCheckout` has no check of its own, so the fan is charged when the provider returns and the Order becomes Paid on a cancelled Event. `Refund all` refunds it. Accepted, to be revisited if a cancellation during an outage ever happens: the check would be the same one as D3.
- [`Issue` for a Won entry already stopped, after 24 hours of provider outage or on a data failure, before the cancellation] → No run is left to reach D3's check, and `EndEnteredByEvent` leaves a Won entry alone, so the entry stays Won with its Order Pending, its card held, and the Event not deletable. An admin was already told when `Issue` stopped, and that state needs handling by hand with or without a cancellation.
- [An admin deletes the Event in the seconds between the end of an entry and the start of its release and notice] → The entry's Order is Void, so `Concert.DeleteAndSuppress` allows it, and the receivers then find no Order: the fan is not told and the hold lapses at the card issuer. Nothing is charged. This exists today for any Lost entry; this change makes it a little more likely because cancelling and deleting come together. Accepted: deletion is one admin's manual step, taken after refunds.
- [An Event with very many Entered entries] → One transaction with one outbox row per entry, longer than the Consumer's 30s `ackWait` only at a size the product does not reach. A redelivery blocks on the stock locks, then changes nothing.

## Migration Plan

1. Release the proto (task group 1) and wait for BSR generation; the backend builds against it.
2. Apply the NACK Consumer before the backend release (task group 2), or the handler has no durable to bind to.
3. Before merging the backend PR, count Entered entries of CANCELLED Events in prod, read-only. Zero is expected: the pilot runs no lottery. If any exist, stop and ask, since `deliverPolicy: new` will not end them.
4. Release the backend. The migration only widens a CHECK, so it is safe with the old code running.

Rollback: revert the backend release. Stored lost reason 3 stays valid under the widened CHECK, and the old code reads an unknown reason as "not drawn" in its wording only.
