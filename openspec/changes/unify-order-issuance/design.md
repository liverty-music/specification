## Context

See proposal.md - Why. After `make-lottery-draw-durable`, `OrderUseCase.Issue` is a workflow for a Won LotteryEntry on the runtime of `introduce-durable-workflows`. Today's first-come paths (backend `origin/main` at `42f2bc78`):

- `CheckoutHandler.Confirm` calls `OrderUseCase.IssueFromCheckout` (`internal/adapter/rpc/checkout_handler.go:106`). It serializes calls per Checkout with `CheckoutRepository.Serialize`, an advisory lock held in a transaction for the whole capture (`order_issue_uc.go:215`, `rdb/checkout_repo.go:510`).
- `IssueDueCheckouts` runs every minute with `ReleaseExpired` in one sweeper goroutine (`internal/di/checkout_sweeper_job.go:34-41`). It finishes Committed Checkouts and reports those charged more than 10 minutes ago with `LogKeyNeedsOperator`.
- `FulfillPayment` (`order_issue_uc.go:376`), called by the webhook (`stripe_webhook_uc.go:249`), issues or finds the Order from the completed-charge notice. It is the only publisher of `ORDER.paid` for a Checkout.
- Every Order has a Settlement since `fix-create-settlement-on-issuance`: `Order.Issue` stores them together. In prod on 2026-10-27, 4 of 4 Orders had a Settlement (read-only count through `db-proxy`).

## Goals / Non-Goals

**Goals:**
- One issuance method for both sources, with the order of steps written in it.
- A fan's mistake (card not yet authenticated, another fan's Checkout) is answered at once and never fixed into a workflow's outcome.

**Non-Goals:**
- `CheckoutUseCase.ReleaseExpired` and `ResaleListingUseCase.RefundSold` stay as they are.
- No change to the Confirm request, its response or the checkout screen's states.

## Decisions

### Check before the workflow, commit inside it

```
fan-api                                   workflow-worker
CheckoutHandler.Confirm
  OrderUseCase.Place(checkout, fan, now)
    Checkout.Get (own Checkout)           PermissionDenied first: a fan never joins
    Order.GetByCheckoutID                  another fan's workflow
    while Held: holding at now, published,
      card authorization Authorized for the amount,
      IdentityVerification when required  FailedPrecondition: the Checkout stays Held
    Workflows.Start Issue                  id issue:<checkout>, queue checkout
    Workflows.Await (30 s)  ------------> Issue(checkout, placed at)      deadline 24 h
                                            step reads: Checkout, TicketType, Organizer, IdentityVerification
                                            step Checkout.Commit(placed at)   NotHeld -> no Order
                                            step Capture                 <- the point of no return
                                              FailedPrecondition -> step RevertCommit -> no Order
                                            step RecordCapture
                                            step CardAuthorization.Get, step Order.Issue
                                            step announce ORDER.paid
```

- **Why the checks run before `Start`**: a workflow runs once per id. If `Issue` checked "card authentication not complete" itself, its first outcome would be fixed for `issue:<checkout>`, and the fan's second try after authenticating would get that old failure. A fan could also join another fan's workflow before the owner check. `Place` checks synchronously, so only a Checkout that can proceed starts a workflow.
- **Why the commit is inside the workflow**: a commit in `Place` followed by a stopped process would leave a Committed Checkout with no workflow and no sweeper to finish it. As the first step of `Issue`, it is recorded and resumed.
- **The placement time is the commit time.** `Checkout.Commit` judges "holding" at the time it is given. The time is the moment the fan placed the order, so the time `Issue` waits in the queue does not count against the hold.
- **`Place` waits 30 seconds** with `Workflows.Await`. A second `Place` for the same Checkout finds it Committed or starts the same id, and waits for the same outcome. This replaces `Serialize` and its transaction held during the capture. After 30 seconds `Place` returns Unavailable and `Issue` goes on; the screen already maps Committed and Completed to "the purchase is being completed" (`route/checkout`).
- **An outcome is a result, not an error.** "Hold already over" and "card no longer chargeable" end `Issue` without an Order and are not reported. `Place` turns them into FailedPrecondition for the fan.

### One workflow, two sources

`OrderUseCase.Issue` takes an `entity.OrderSource` (exactly one of a LotteryEntry id or a Checkout id with its placement time). The steps differ only before the capture and in the compensation:

| Step | LotteryEntry | Checkout |
|---|---|---|
| Precondition | the entry is Won | checked by `Place` |
| Before the charge | nothing | `Checkout.Commit` |
| Capture cannot succeed | `LotteryEntry.RevertWin` | `Checkout.RevertCommit` |
| After the charge | `Order.Issue` | `Checkout.RecordCapture`, then `Order.Issue` |
| Then | announce `ORDER.paid` | announce `ORDER.paid` |

- **Its own queue**: `checkout`, global concurrency 2. A large lottery's `Issue` runs on the `payment` queue, so a fan waiting on the screen never waits behind it.
- Rejected: a `CheckoutUseCase.Confirm` that commits and then starts `Issue`. It puts the commit outside the workflow (above), and a usecase does not call another usecase's method (the spec rule for `components/usecase`).

### The completed-charge notice

`payment_intent.succeeded` is acknowledged without effect for every source. The capture is the response to the platform's own call, and `Issue` announces the Order. `processed_webhook_events` still records the notice, so a redelivery stays a no-op. Rejected: starting `issue:<source>` from the notice as a safety net. Every capture the platform makes runs inside `Issue`, so the start would always find the workflow, and a capture made outside the platform (in the Stripe dashboard) has no Checkout step to resume.

### Every Order has a Settlement

`Order.Issue` stores the Order, its Tickets and its Held Settlement together, and production holds no Order without one. The branches that treated a missing Settlement as normal go:

- `Refund` no longer claws back nothing for an Order without a Settlement. A missing Settlement now fails the refund, so broken data is not refunded silently.
- `GetWithSettlement` and the admin `OrderService.Get` return Internal instead of the Order alone.
- The Settlement entity's ER diagram becomes `Order ||--|| Settlement` (Purpose, edited at archive).

A Settlement stays in the same transaction as the Order: created later, it would miss a resale that already reduced it, could be created for a Refunded Order and paid out, and would take the fee rate of a later time.

## Risks / Trade-offs

- [A Committed Checkout exists at the moment of the rollout, left by an interrupted old call] → Before the deploy, list Committed Checkouts read-only in prod; none is expected (no users). If one exists, finish it with the old code before deploying.
- [`ReleaseExpired` can expire a Checkout whose order was placed in its last seconds, before `Issue` commits] → The `checkout` queue starts `Issue` within about a second. The fan then sees "the 15 minutes passed", and the card is not charged.
- [The 30-second wait holds a request goroutine] → It holds no database connection: `Await` polls the workflow status.

## Migration Plan

1. backend: `Place`; `Issue` for a Checkout and the `checkout` queue; the handler change; the Settlement branches; removal of `IssueFromCheckout`, `IssueDueCheckouts`, `FulfillPayment`, `Serialize` (its only caller goes) and the issuance call in the checkout sweeper.
2. Read-only prod check for Committed Checkouts, deploy, confirm the rollout, and buy one ticket with the Stripe Sandbox E2E.

Rollback: revert the backend release; Checkouts and Orders keep their shape.
