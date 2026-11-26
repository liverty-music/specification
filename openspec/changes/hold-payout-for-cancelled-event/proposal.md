## Why

A cancelled concert is still paid out. `SettlementUseCase.ReleaseDueSettlements` pays every Held Settlement whose event started more than 7 days ago, and nothing looks at whether the Event is CANCELLED. Cancelling an Event does not touch its Settlements, and the 中止 (cancellation) refund is a manual admin step (`Refund all`). If nobody runs it in time, the Organizer is paid for a concert whose fans were told they would be refunded, and a later refund has to claw the payout back, with the platform bearing any negative balance.

The owner decided on 2026-11-26 (liverty-music/specification#996, first item; pilot plan #1074) that a Settlement of a CANCELLED Event is never released and that the refund stays manual. It must ship before the pilot sells for real money.

## What Changes

- A Settlement is not eligible for release when its Event is CANCELLED, however long after the start time.
- `ReleaseDueSettlements` reads each Event's publish state on every run and withholds the payout of a CANCELLED Event. The Settlement stays Held.
- Nothing else changes: `Refund all` still refunds each Paid Order and makes its Held Settlement Reversed; a Settlement already Released is still clawed back by the refund. One limit remains: a payout that was made but not recorded before the cancellation stays unrecorded, and the refund does not claw it back (design Risks). No automatic refund, no new Settlement status, no new alert, no screen change, no proto change and no migration.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/entity/settlement` (Purpose): "Release eligibility" also requires that the event is not CANCELLED. The attribute table's `event` row says so at archive.
- `components/usecase/settlement/release-due-settlements` (Purpose): reads the Event with `Event.Get` and withholds the Settlement of a CANCELLED Event. The Purpose sentence and the sequence diagram are updated at archive.
- `stories/remove-a-cancelled-concert` (Purpose): a cancelled concert is never paid out, before or after its refunds. The event-modeling diagram gains the release schedule at archive.

Entity operations relied on and unchanged: `Event.Get` already returns the publish state CANCELLED; `Event.GetEventStartTime` still supplies the start time; `Settlement.ListHeld` still returns every Held Settlement; `Order.Get`, the payout account operations, `Settlement.CreatePayout` and `Settlement.MarkReleased` keep their promises. `OrderUseCase.Refund` and `Order.CommitRefund` already make a Held Settlement Reversed without a payout reversal, and `Concert.Delete` already refuses an Event with a Settlement that is not Reversed.

## Impact

- backend: the release eligibility rule, the payout sweep and its wiring in the workflow worker, and their tests. No schema change.
- specification: the specs above, and the money-flow topic page at archive.
- frontend, cloud-provisioning, proto: none.
- Sequencing: the backend change is merged only after backend release 2 of `globalize-venues` has been released, because both change the payout sweep's release gate.
