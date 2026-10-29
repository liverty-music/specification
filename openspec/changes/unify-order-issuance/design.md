## Context

See proposal.md - Why. This change is written on the model of `remodel-ticket-sales`: an Order is created Pending when the fan applies, a Checkout holds a FirstCome sale's TicketStock for its Order and names its sale, and official resale is not bought through a Checkout. After `make-lottery-draw-durable`, `OrderUseCase.Issue` is a workflow that makes a Won LotteryEntry's Pending Order Paid, on the runtime of the archived `introduce-durable-workflows`.

The first-come paths it replaces (backend `origin/main` at `42f2bc78`, before `remodel-ticket-sales`):

- `CheckoutHandler.Confirm` calls `OrderUseCase.IssueFromCheckout` (`internal/adapter/rpc/checkout_handler.go:106`). It serializes calls per Checkout with `CheckoutRepository.Serialize`, an advisory lock held in a transaction for the whole capture (`order_issue_uc.go:215`, `rdb/checkout_repo.go:510`).
- `IssueDueCheckouts` runs every minute with `ReleaseExpired` in one sweeper goroutine (`internal/di/checkout_sweeper_job.go:34-41`). It finishes Committed Checkouts and reports those charged more than 10 minutes ago with `LogKeyNeedsOperator`.
- `FulfillPayment` (`order_issue_uc.go:376`), called by the webhook (`stripe_webhook_uc.go:249`), issues or finds the Order from the completed-charge notice. It is the only publisher of `ORDER.paid` for a Checkout.
- Every Order has had a Settlement since `fix-create-settlement-on-issuance`: `Order.Issue` stores them together. In prod on 2026-10-27, 4 of 4 Orders had a Settlement (read-only count through `db-proxy`). After `remodel-ticket-sales` this holds for Paid and Refunded Orders; Pending and Void Orders were never paid and have none.

## Goals / Non-Goals

**Goals:**
- One issuance method for both sources, with the order of steps written in it.
- A fan's mistake (card not yet authenticated, another fan's Checkout) is answered at once and never fixed into a workflow's outcome.

**Non-Goals:**
- `CheckoutUseCase.ReleaseExpired` stays as it is: it makes an expired Checkout Expired and its Order Void, and gives back the card authorization.
- No change to the Confirm request, its response or the checkout screen's states.
- Official resale: it is bought through a resale entry and its draw (`resell-tickets-by-lottery`), not through a Checkout.
- `Issue` never refunds on its own and there is no Order status for a charge it could not issue: a run that cannot issue after charging stops after 24 hours with the Order Pending and is reported to an admin.

## Decisions

### Check before the workflow, commit inside it

```
fan-api                                   workflow-worker
CheckoutHandler.Confirm
  OrderUseCase.Place(checkout, fan, now)
    Checkout.Get, Order.Get (own Order)   PermissionDenied first: a fan never joins
                                           another fan's workflow
    Expired or Released: FailedPrecondition
    while Held: holding at now, published,
      Order's card authorization Authorized for its amount,
      IdentityVerification when required  FailedPrecondition: Checkout Held, Order Pending
    Workflows.Start Issue                  id issue:checkout:<checkout>, queue checkout
    Workflows.Await (30 s)  ------------> Issue(checkout)                 deadline 24 h
                                            step reads: Checkout, Order, TicketStock, TicketSale,
                                                        Organizer, IdentityVerification
                                            step Checkout.Commit(now)    NotHeld -> end
                                            step Capture                 <- the point of no return
                                              FailedPrecondition -> step RevertCommit (Order Void) -> end
                                            step RecordCapture
                                            step CardAuthorization.Get, step Order.Issue (Order Paid)
                                            step announce ORDER.paid
```

- **Why the checks run before `Start`**: a workflow runs once per id. If `Issue` checked "card authentication not complete" itself, its first outcome would be fixed for that id, and the fan's second try after authenticating would get that old failure. A fan could also join another fan's workflow before the owner check. `Place` checks synchronously, so only a Checkout that can proceed starts a workflow.
- **Why the commit is inside the workflow**: a commit in `Place` followed by a stopped process would leave a Committed Checkout with no workflow and no sweeper to finish it. As the first step of `Issue`, it is recorded and resumed.
- **The commit time is the time the step runs, never the placement time.** `Checkout.Commit` judges "holding" at the time it is given. Backdating it to the placement time let a hold that lapsed while `Issue` waited in the queue be committed after `CheckoutUseCase.Start` had already sold its tickets to another fan (a lapsed hold no longer counts in the stock), overselling the TicketStock. The queue starts `Issue` within about a second, so only an order placed in the last second of its hold can miss it; the fan is then told the 15 minutes passed (Risks).
- Rejected — commit synchronously in `Place` and hand only the charge to `Issue`: a process that stops between that commit and starting the workflow would leave a Committed Checkout that nothing finishes, which is what the removed sweeper existed for.
- **`Place` waits 30 seconds** with `Workflows.Await`. A second `Place` for the same Checkout finds it Committed or starts the same id, and waits for the same outcome. This replaces `Serialize` and its transaction held during the capture. After 30 seconds `Place` returns Unavailable and `Issue` goes on; the screen already maps Committed and Completed to "the purchase is being completed" (`route/checkout`).
- **An outcome is a result, not an error.** "Hold already over" and "card no longer chargeable" end `Issue` without a Paid Order and are not reported. `Place` turns them into FailedPrecondition for the fan.

### One workflow, two sources

`OrderUseCase.Issue` takes an `entity.OrderSource` (exactly one of a LotteryEntry id or a Checkout id). Both make the source's Pending Order Paid; the steps differ only before the capture and in the compensation:

| Step | LotteryEntry | Checkout |
|---|---|---|
| Precondition | the entry is Won | checked by `Place` |
| Before the charge | nothing | `Checkout.Commit` |
| Capture cannot succeed | `LotteryEntry.RevertWin` (Order Void) | `Checkout.RevertCommit` (Order Void) |
| After the charge | `Order.Issue` | `Checkout.RecordCapture`, then `Order.Issue` |
| Then | announce `ORDER.paid` | announce `ORDER.paid` |

- **Workflow id** `issue:checkout:<checkout id>` and `issue:entry:<entry id>`, so the two sources never share an id.
- **Its own queue**: `checkout`, global concurrency 2. A large lottery's `Issue` runs on the `payment` queue, so a fan waiting on the screen never waits behind it.
- Rejected: a `CheckoutUseCase.Confirm` that commits and then starts `Issue`. It puts the commit outside the workflow (above), and a usecase does not call another usecase's method (the spec rule for `components/usecase`).

### The completed-charge notice

`payment_intent.succeeded` is acknowledged without effect for every source. The capture is the response to the platform's own call, and `Issue` announces the Order. `processed_webhook_events` still records the notice, so a redelivery stays a no-op. Rejected: starting `Issue` from the notice as a safety net. Every capture the platform makes runs inside `Issue`, so the start would always find the workflow, and a capture made outside the platform (in the Stripe dashboard) has no Checkout step to resume.

### A Paid Order has its Settlement

`Order.Issue` makes the Order Paid and stores its Tickets and Held Settlement together, so no Paid or Refunded Order lacks a Settlement. The branches that treated a missing Settlement as normal go for those Orders:

- `Refund` (only Paid Orders are refundable) fails when the Settlement cannot be read, so broken data is not refunded silently.
- `GetWithSettlement` and the admin `OrderService.Get` return the Order alone only for a Pending or Void Order, without reading a Settlement; for a Paid or Refunded Order a missing Settlement is Internal.
- The Settlement entity's ER diagram becomes `Order ||--o| Settlement`, with the Purpose saying a Paid Order has exactly one (edited in the main spec with this change).

A Settlement stays in the same transaction as making the Order Paid: created later, it would miss a resale that already reduced it, could be created for a Refunded Order and paid out, and would take the fee rate of a later time.

## Risks / Trade-offs

- [A Committed Checkout exists at the moment of the rollout, left by an interrupted old call] → Before the deploy, list Committed Checkouts read-only in prod; none is expected (no users, and `remodel-ticket-sales` deletes the existing ticket data). If one exists, finish it with the old code before deploying.
- [`ReleaseExpired` can expire a Checkout whose order was placed in its last seconds, before `Issue` commits] → The `checkout` queue starts `Issue` within about a second. The fan then sees "the 15 minutes passed", the Order is Void and the card is not charged.
- [The 30-second wait holds a request goroutine] → It holds no database connection: `Await` polls the workflow status.

## Migration Plan

1. backend: `Place`; `Issue` for a Checkout and the `checkout` queue; the handler change; the Settlement branches; removal of `IssueFromCheckout`, `IssueDueCheckouts`, `FulfillPayment`, `Serialize` (its only caller goes) and the issuance call in the checkout sweeper.
2. Read-only prod check for Committed Checkouts and Paid Orders without a Settlement, deploy, confirm the rollout, and buy one ticket with the Stripe Sandbox E2E.

Rollback: revert the backend release; Checkouts and Orders keep their shape.
