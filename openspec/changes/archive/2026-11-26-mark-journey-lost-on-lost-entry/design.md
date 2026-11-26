## Context

See proposal.md. Backend records Applied from `LOTTERY_ENTRY.entered` (`TicketJourneyUseCase.MarkApplied`, JetStream durable `mark-ticket-journey-applied`) and Paid from the paid Order. `LOTTERY_ENTRY.lost` is already published and consumed by `send-lottery-loss`, `start-lottery-entry-workflow` and `track-lottery-entry-result`. `(*TicketJourney).ReplaceableBy` lets any platform status other than Applied replace any journey.

## Goals / Non-Goals

**Goals:** record the loss from the existing announcement, without overwriting what the fan knows better.

**Non-Goals:** resale entries; backfilling past losses; screen changes.

## Decisions

- **A consumer of `LOTTERY_ENTRY.lost`, not a step of the draw.** Same shape as MarkApplied: a journey failure must not fail or delay a draw. Durable `mark-ticket-journey-lost`, settings copied from `consumer-mark-ticket-journey-applied` (`deliverPolicy: new`, so past losses are not replayed).
- **The lost reason comes from the announcement.** Lost is final, so the entry is not read again. The announcement carries only the entry, so MarkLost reads its Order and that Order's TicketStock for the user and the event.
- **Only another open lottery entry holds the record back** (`LotteryEntry.ListByUser`, then `TicketStock.Get` for the other Entered or Won entries). That entry's result is announced and runs MarkLost or MarkPaid, which decides the journey, unless the concert is cancelled, which records nothing. Alternative: `Order.GetHeldForEvent > 0`; rejected because it also counts checkouts and resale entries, whose end runs nothing, leaving Applied forever. A Paid journey is protected by the replacement rule.
- **The replacement rule lives in `ReplaceableBy`.** Platform Lost: replace Tracking or Applied only. Tracking is included for a fan whose Applied was never recorded because the entry announcement arrived after the draw.
- **No guard across the check and the write.** MarkLost and MarkApplied each read lottery entries and then write the journey as separate steps, which leaves two races, both accepted:
  - MarkLost overwrites a new Applied: an entry for the same event is created, and its MarkApplied finishes, between MarkLost's read of the entries and its write. Sales of one event never overlap (`usecase/ticket-sale/create`), so this needs the next sale to be open before the loss is processed (a sale that starts before the draw, or a late draw, charge or consumer), and then the whole entry within milliseconds.
  - MarkApplied overwrites a new Lost: MarkApplied reads the entry as Entered, and the draw and MarkLost both finish before its write. The draw starts at least one minute after the sale ends, so MarkApplied must be that late and then stall for the whole chain between its two steps.

  Either way only the journey is stale: the fan can set it by hand, and a later entry or purchase writes Applied or Paid. Closing both would need the journey write to re-read lottery entries in its transaction while it holds the journey row, which is not worth the cross-table read, the extra operation and the concurrency tests.

- **No per-entry guard against a repeated delivery.** MarkLost stores no record that an entry's loss was applied; the replacement rule makes a second run a no-op only while the journey is still Lost. If the fan sets Tracking or Applied, or removes the journey, and the same announcement is then delivered again (a stop between the write and the ack, or an expired ack wait), Lost is recorded again. The same happens when the first run was held back by another open entry that has since ended because the concert was cancelled. Accepted as MarkApplied accepts the same: only the journey is stale and the fan can set it again. A guard would need a new stored time on the lottery entry, a migration and an entity operation.

## Risks / Trade-offs

- [The two races and the repeated delivery above] → accepted; see the last two decisions.
- [Deploy order] the consumer must exist before the backend binds it → cloud-provisioning merges first. Losses announced between the two wait on the durable and are handled at rollout.

## Migration Plan

cloud-provisioning (consumer, scaler), then the backend release. Rollback: revert the backend release; the unused durable holds messages harmlessly until removed.
