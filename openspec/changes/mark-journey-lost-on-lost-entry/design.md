## Context

See proposal.md. Backend records Applied from `LOTTERY_ENTRY.entered` (`TicketJourneyUseCase.MarkApplied`, JetStream durable `mark-ticket-journey-applied`) and Paid from the paid Order. `LOTTERY_ENTRY.lost` is already published and consumed by `send-lottery-loss`, `start-lottery-entry-workflow` and `track-lottery-entry-result`. `(*TicketJourney).ReplaceableBy` lets any platform status other than Applied replace any journey.

## Goals / Non-Goals

**Goals:** record the loss from the existing announcement, without overwriting what the fan knows better.

**Non-Goals:** resale entries; backfilling past losses; screen changes.

## Decisions

- **A consumer of `LOTTERY_ENTRY.lost`, not a step of the draw.** Same shape as MarkApplied: a journey failure must not fail or delay a draw. Durable `mark-ticket-journey-lost`, settings copied from `consumer-mark-ticket-journey-applied` (`deliverPolicy: new`, so past losses are not replayed).
- **The lost reason comes from the announcement.** Lost is final, so the entry is not read again. The handler resolves the user and event from the Order and its TicketStock, as the MarkApplied consumer's data does.
- **"Still has something open" is `Order.GetHeldForEvent > 0`.** It already counts Issued tickets and Pending Orders of open Checkouts, lottery entries and resale entries, and excludes the entry just lost. Alternative: a new query over entries only; rejected as a second definition of the same fact.
- **The replacement rule lives in `ReplaceableBy`.** Platform Lost: replace Tracking or Applied only. Tracking is included for a fan whose Applied was never recorded because the entry announcement arrived after the draw.
- **No lock across the check and the write.** `GetHeldForEvent` and the journey upsert are separate steps. A new entry for the same event created between them, whose MarkApplied also runs between them, would be overwritten with Lost. Locking would need entry creation to lock the journey row, coupling the purchase path to the journey. The window is milliseconds, the fan can set the status by hand, and a later entry or purchase writes Applied or Paid again.

## Risks / Trade-offs

- [The race above] → accepted; see the last decision.
- [Deploy order] the consumer must exist before the backend binds it → cloud-provisioning merges first. Losses announced between the two wait on the durable and are handled at rollout.

## Migration Plan

cloud-provisioning (consumer, scaler), then the backend release. Rollback: revert the backend release; the unused durable holds messages harmlessly until removed.
