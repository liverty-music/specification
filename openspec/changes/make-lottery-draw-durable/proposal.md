## Why

The lottery draw charges before it records. `LotteryEntryUseCase.RunDraw` draws in a fresh random order, captures every winner and releases every loser, and only then records the outcome in one transaction. If the process stops between the first capture and that record, the next run draws again in a new random order. A fan who was already charged can then lose, and their release fails because the card authorization is already captured, so the fan is charged without tickets. Every step after the draw (the capture, the issuance by a 1-minute sweeper, the release) is recovered by its own sweeper or not at all, and a Stripe outage during the draw turns every winner into a loser. This change records the outcome of the draw first and once, and runs each later step for each entry on a durable execution engine (DBOS Transact Go, in the application's own Postgres), so a stopped step resumes where it stopped. It also gives the platform the engine that the first-come checkout moves to next (`unify-order-issuance`). It builds on `remove-lottery-entry-withdrawal`.

## What Changes

- The draw records Won and Lost, with each entry's draw position, for each TicketType in one step, before any card is charged. The draw of a TicketType that is already recorded keeps its outcome, so a stopped draw resumes with the same winners. The draw itself charges and releases nothing.
- A Won entry means the draw allocated its tickets; it is charged afterwards. **BREAKING** (for readers of the state): Won no longer implies a captured card authorization.
- For each Won entry, `OrderUseCase.Issue` captures the card authorization, then issues the Order, its Tickets and its Settlement, and announces the Order as paid. A capture that fails because the payment provider cannot be reached is tried again for up to 24 hours. A card authorization that can no longer be captured makes the entry Lost again (`LotteryEntry.RevertWin`) and is released. It replaces `IssueFromCapturedWin` and the `IssueDueWins` sweeper.
- For each Lost entry and each unconfirmed Draft, `CardAuthorizationUseCase.Release` releases the card authorization, trying again for up to 24 hours, and reports a captured one to an admin.
- `LotteryEntryUseCase.Draw` replaces `RunDraw`. `DrawDueSales` keeps its 1-minute schedule.
- `OrderUseCase.FulfillPayment` no longer issues or announces for a won lottery entry: the completed-charge notice of a lottery capture is acknowledged without effect, because `Issue` already announced the Order.
- New backend dependency: DBOS Transact Go. Its system tables live in a `dbos` schema of the same Cloud SQL database and are created by the Atlas migrations; only the fan workload runs workflows.

## Capabilities

### New Capabilities

- `components/entity/lottery-entry/record-draw-outcome`: records one TicketType's Won and Lost entries with their draw positions, once.
- `components/entity/lottery-entry/revert-win`: makes a Won entry with no Order Lost.
- `components/entity/ticket-sale/record-draw`: records the time a sale's draw completed.
- `components/usecase/lottery-entry/draw`: draws one closed sale, TicketType by TicketType, without charging.
- `components/usecase/order/issue`: charges a Won entry and issues its Order, Tickets and Settlement.
- `components/usecase/card-authorization/release`: releases the card authorization of a Lost entry or an unconfirmed Draft.

### Modified Capabilities

- `components/entity/lottery-entry` (Purpose): the state diagram gains Won to Lost; Won means the draw allocated the tickets, not that the card was charged.
- `components/entity/lottery-entry/persist-draw-outcome`: removed, replaced by `record-draw-outcome` and `ticket-sale/record-draw`.
- `components/entity/order/list-lottery-entry-ids-awaiting-issuance`: removed; its only caller, `IssueDueWins`, goes.
- `components/usecase/lottery-entry/run-draw`: removed, replaced by `draw`.
- `components/usecase/lottery-entry/draw-due-sales`: runs `Draw`; a stopped draw resumes.
- `components/usecase/order/issue-from-captured-win`: removed, replaced by `issue`.
- `components/usecase/order/issue-due-wins`: removed; `issue` runs for each Won entry and resumes on its own.
- `components/usecase/order/fulfill-payment`: a lottery charge is acknowledged without effect.
- `stories/win-tickets-in-a-lottery` (Purpose): the usecase diagram names `Draw`, `DrawDueSales`, `OrderUseCase.Issue` and `CardAuthorizationUseCase.Release`. A requirement is added for a draw that stops midway.

Unchanged and why: `components/entity/order/issue` already stores the Order, its Tickets and its Settlement together and fails with AlreadyExists for a second Order of the same source; `components/entity/card-authorization/capture` and `release` already succeed again for a repeated call; `components/entity/lottery-entry/list-undrawn-for-ticket-type` and `run-lottery-draw` keep their contracts; `components/entity/ticket-sale/list-due-for-draw` keeps selecting closed sales without a draw time.

## Impact

- **backend**: adds `github.com/dbos-inc/dbos-transact-golang`; a workflow interface in the usecase layer with a DBOS implementation in infrastructure; replaces `RunDraw`, `IssueFromCapturedWin`, `IssueDueWins` and the lottery draw and issuance sweeper goroutines; an Atlas migration that creates the `dbos` schema and grants it to the fan workload.
- **cloud-provisioning**: the fan workload's database pool settings for the DBOS pool.
- **Observability**: DBOS Go has no OpenTelemetry instrumentation; the workflow implementation carries the W3C trace context that `fix-trace-propagation` established.
- **Operations**: stopped workflows are found and resumed with the DBOS CLI against the prod database through the `db-proxy` runbook.
- **Not in this change**: the first-come checkout (`unify-order-issuance`), the other sweepers (`ReleaseExpired`, `RefundSold`, `ReleaseDueSettlements`, the organizer reconciler), and promotion of a loser (繰上げ, still not done).
