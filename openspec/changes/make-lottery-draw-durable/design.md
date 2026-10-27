## Context

See proposal.md - Why. Facts this design depends on (backend `origin/main` at `42f2bc78`, after `enter-lottery-at-confirm`):

- **The draw today** (`internal/usecase/lottery_entry_uc.go:385-466`): `RunDraw` lists each TicketType's Entered entries, computes `RunLotteryDraw(…, uc.newRand())`, captures each winner and releases each loser in the loop, and only then calls `PersistDrawOutcome` (`:450`). A release failure is only logged (`release`). Each entry's result is published as `ORDER.lottery_entry_drawn` with `CaptureFailed` (`entity/event_data.go:136`) for product analytics.
- **PersistDrawOutcome** (`infrastructure/database/rdb/lottery_entry_repo.go:216-275`) updates the given entries by id without checking their state (`lotteryEntrySetOutcomeQuery`, `:88-93`) and sets `ticket_sales.draw_at` last, in one transaction.
- **Sweepers**: `DrawDueSales` and `IssueDueWins` run every minute as goroutines in the fan workload (`internal/di/provider.go:521-548`).
- **Stripe keys**: capture and cancel send a fixed key per operation and card authorization (`infrastructure/payment/stripe_card_authorization.go:188`, `:225`), and decide the outcome by reading the PaymentIntent after an error (`:184-217`). stripe-go v87 sends a new random key on a write call without one and keeps it for its own retries (`stripe.go:873-881`, 2 retries by default, `:51`).
- **Stripe's rules** ([Idempotent requests](https://docs.stripe.com/api/idempotent_requests), [Advanced error handling](https://docs.stripe.com/error-low-level)): a key identifies one operation; API v1 returns the saved first response to every retry with the same key, "including `500` errors", for at least 24 hours; after a 500, resolve the outcome by retrieving the object before using a new key.
- **Notices to fans**: a won entry's Order is announced as `ORDER.paid`, and `SendOrderConfirmation` sends an email and an `order_confirmation` push. A losing fan receives nothing today. Notification types are strings (`entity/notification.go:21`; `notifications.type` comment, `schema.sql:380`). `orders.confirmation_send_at` keeps the confirmation email to one per Order (`schema.sql:880`).
- **Workflow runtime** (`introduce-durable-workflows`): `Flow` and `Workflows` in the usecase layer, the `workflow-worker` Deployment, step retries on Unavailable and DeadlineExceeded, stored deadlines, the "Workflow Needs Admin" alert, and an event id derived from the workflow id and the step.

## Goals / Non-Goals

**Goals:**
- A draw that stops anywhere resumes with the same winners, and no fan is charged without tickets.
- Every result reaches the fan: a winner by the confirmation email and push, a loser by a loss email and push.
- The order of the steps reads in the usecase methods, and each entity operation keeps one responsibility.

**Non-Goals:**
- The first-come checkout (`unify-order-issuance`).
- Promotion of a loser (繰上げ).
- A time bound for the result. The spec says only that the draw runs after the window closes and the fan is told.

## Decisions

### Record first, then one workflow per entry

```
schedule draw-due-sales (* * * * *)
  DrawDueSales                       step ListDueForDraw
                                     Start Draw(sale)                  id draw:<sale>
Draw(sale)                           step TicketSale.Get
                                     step "draw <ticket type>" per TicketType:
                                          ListUndrawnForTicketType + RunLotteryDraw (random order recorded once)
                                     step PersistDrawOutcome(sale, winners, losers)      one transaction
                                     Start Issue(entry)                   id issue:<entry>    per Won entry
                                     Start ReleaseCardAuthorization(entry) id release:<entry> per Lost entry
                                     step announce lottery result        per entry
Issue(entry)                deadline 24 h
                                     step reads: GetByLotteryEntryID, LotteryEntry.Get (Won),
                                          TicketType.Get, Event.GetOrganizerID, Organizer.Get, IdentityVerification
                                     step Capture                     <- the point of no return
                                       FailedPrecondition -> step RevertWin
                                                             Start ReleaseCardAuthorization(entry)
                                                             step announce lottery result Lost (failed capture)
                                                             end: no Order (a result, not an error)
                                     step CardAuthorization.Get (captured payment)
                                     step Order.Issue (Order, Tickets, Held Settlement)
                                     step announce ORDER.paid
ReleaseCardAuthorization(entry) deadline 24 h
                                     step LotteryEntry.Get (Lost)
                                     step CardAuthorization.Release
```

- **The outcome of a sale is one transaction, as today.** The random order is fixed by its step, so a resumed draw records the same outcome; splitting the record per TicketType would add a half-drawn state for nothing. `PersistDrawOutcome` gains one rule: when the sale already has a draw time, it changes nothing. A step that ran its transaction but stopped before its result was recorded runs again, and must not undo a `RevertWin` made after it.
- **Every read that can fail for a data reason runs before the capture.** After the capture only `CardAuthorization.Get`, `Order.Issue` and the announcement remain, and each of them only fails transiently. A fan is never charged and then stopped by a missing Organizer or IdentityVerification.
- **A card that can no longer be charged is a result.** Per the failure classification of `introduce-durable-workflows`, `Issue` returns "no Order" instead of an error, so it is not reported. `ReleaseCardAuthorization` ending with FailedPrecondition (a Lost entry whose card was charged) is an error and is reported.
- **Starting another usecase's workflow is a command, not a call.** `Draw` starts `OrderUseCase.Issue` by name and id through `Flow.Start`, which is recorded as a step and runs once per id. The specs write it as the trigger of the started method ("Issue SHALL run once for each entry that PersistDrawOutcome records Won"), the rule for internal events in the spec schema. A NATS event was rejected for this hand-off: it would need its own consumer and its own deduplication for a command that has exactly one receiver.
- **`ReleaseCardAuthorization` is on `LotteryEntryUseCase`.** It acts for a Lost entry and reads its state. A `CardAuthorizationUseCase` would hold one method.
- **Ids**: `draw:<sale>`, `issue:<entry>`, `release:<entry>`. A schedule run that lists a sale whose draw is still running, or ended in ERROR, starts nothing new (`DrawDueSales` "Drawn once", "One sale fails").
- **Deadlines**: 24 hours for `Issue` and `ReleaseCardAuthorization` (`WithDeadline`). A JPY card authorization lasts 30 days (`docs/payments-design.md`), so a resumed capture still finds it. `Draw` has no deadline: it only reads and writes the database.

### Telling the fan

- **Winner**: `Issue` announces `ORDER.paid`, and `SendOrderConfirmation` sends the email and the push it sends today. For an Order whose source is a LotteryEntry, the email first says the entry won, and the push says "当選しました". A separate "won" message at the draw was rejected: it would be sent before the charge, and a card that cannot be charged would then need a correction.
- **Loser**: the `ORDER.lottery_entry_drawn` event that product analytics reads today is the lottery result announcement. `SendLotteryLoss` runs in the event consumer for each Lost result and sends an email (`LotteryEntry.SendLossEmail`, one per entry through the new `lottery_entries.loss_email_send_at`) and a `lottery_loss` push that opens the event page. The message says whether the entry was not drawn or the win was cancelled because the card could not be charged (`CaptureFailed`).
- The announcement is published from a step, so it keeps one id across a resumed run, and product analytics and the email see it once.

### Stripe keys: the operation, not the run

A key names one business operation. What prevents a second effect differs by operation, and so does the key:

| Operation | What prevents a second effect | Key |
|---|---|---|
| Capture, cancel | The PaymentIntent: it is captured or cancelled at most once | None of ours: stripe-go's key per call. The outcome is read from the PaymentIntent |
| Create a card authorization (checkout) | Nothing on Stripe's side: PaymentIntents can be created any number of times | The Checkout id, as today |
| Refund, transfer (later changes) | Nothing on Stripe's side | The business id (`refund:<order>`, `transfer:<split>`); after a 500, reconcile by metadata before a new key |

- **Why the fixed capture and cancel keys go**: Stripe saves a 500 under the key and returns it to every retry for at least 24 hours. A capture that once got a 500 fails on every retry of the step until Issue's 24-hour deadline, even after Stripe recovers. Capture reads the PaymentIntent after every error, which is the reconciliation Stripe asks for before a new key, and a PaymentIntent can be captured only once, so a fresh key per call cannot charge twice. The same holds for cancel. This also brings the code back to the existing contract "the outcome SHALL follow the CardAuthorization's status, not the outcome of an earlier request".
- **Why not a key from the workflow id and the step**: the step id is the step's position, so it changes when a patch adds a step, and an admin's `fork` runs under a new workflow id. Such a key repeats a cached 500 exactly like the fixed key, and names the run instead of the operation. The DBOS docs make the workflow id an idempotency key because it is derived from an order or request id (`golang/tutorials/workflow-management.md:135`); the business id itself is the better key wherever one exists, and every Stripe call here has one or needs none.

### Queue

One queue `payment` with a global concurrency of 2 for `Issue` and `ReleaseCardAuthorization`. The worker's pool has 5 connections, shared with DBOS (`introduce-durable-workflows` "Connections"). Each step holds at most one connection, so 2 running workflows leave room for DBOS and `Draw`. Stripe's live-mode limit (100 requests per second) is far above what 2 workflows send, so no rate limiter is set. `Draw` and `DrawDueSales` run outside the queue, started by the schedule and by `Draw` itself.

### FulfillPayment for lottery charges

The `payment_intent.succeeded` notice of a lottery capture arrives after `Issue` captured. `FulfillPayment` finds the LotteryEntry and returns without effect, so the Order is announced once, by `Issue`. The capture is the response to the platform's own call, so issuance does not wait for the notice (Stripe retries it for up to 3 days).

## Risks / Trade-offs

- [A Won entry has no Order for a few seconds, and for up to 24 hours while Stripe is down] → Readers that need a paid purchase read the Order (`Order.GetByLotteryEntryID`), and the organizer's stats count Won as allocated. An Issue that passes its deadline is reported by "Workflow Needs Admin".
- [Workflow code changed without `Patched` breaks resumed runs] → The AGENTS.md rules of `introduce-durable-workflows`. The story test resumes a run recorded by the previous code.
- [A loss email is sent before the release finishes] → The message says the amount held "is given back" and may show for a few days. A release that never succeeds is reported to an admin.

## Migration Plan

1. backend: capture and cancel without a fixed idempotency key; migration for `lottery_entries.loss_email_send_at` and the `notifications.type` comment; `PersistDrawOutcome`'s draw-time rule; `RevertWin`, `SendLossEmail`; `Draw`, `ReleaseCardAuthorization`, `Issue`, `SendLotteryLoss` and the `payment` queue; the `draw-due-sales` schedule in the worker; removal of `RunDraw`, `IssueFromCapturedWin`, `IssueDueWins`, `ListLotteryEntryIDsAwaitingIssuance` and the two goroutines.
2. Before the deploy, read-only in prod: list Lottery sales due for a draw and Won entries without an Order. Both are expected to be empty (no users). A due sale is drawn by the new schedule after the deploy. A Won entry without an Order has no trigger in the new code: if one exists, stop and issue it with the old code first.
3. Deploy, then confirm the AtlasMigration, the rollout, and a `draw-due-sales` run for each minute since the rollout.

Rollback: revert the backend release. The new column stays unused; no business table changes shape.
