## Context

See proposal.md - Why. After `make-lottery-draw-durable`, the backend has the workflow interface (`internal/usecase/workflow.go`), its DBOS implementation, and `OrderUseCase.Issue` as a workflow for a LotteryEntry. Today's first-come paths:

- `CheckoutHandler.Confirm` calls `OrderUseCase.IssueFromCheckout` (`internal/adapter/rpc/checkout_handler.go:106`), which serializes calls per Checkout with `CheckoutRepository.Serialize` (an advisory lock held in a transaction during the capture, `rdb/checkout_repo.go:481-497`).
- `IssueDueCheckouts` runs every minute in the fan workload (`internal/di/checkout_sweeper_job.go:34-41`), finishes Committed Checkouts and reports those charged for more than 10 minutes with `LogKeyNeedsOperator`.
- `FulfillPayment` (`usecase/order_issue_uc.go:376-389`) issues or finds the Order from the completed-charge notice and is the only publisher of `ORDER.paid` for a Checkout.

## Goals / Non-Goals

**Goals:**
- One issuance method for both sources, with each source's own preconditions and compensation.

**Non-Goals:**
- `CheckoutUseCase.ReleaseExpired`, `ResaleListingUseCase.RefundSold` and their sweepers stay as they are.
- No change to the Confirm request, its response or the checkout screen's states.

## Decisions

### One workflow, two sources

`OrderUseCase.Issue` takes an `entity.OrderSource` (exactly one of a LotteryEntry id or a Checkout id, as the Order's source attribute already is). Its steps differ only before the capture and in the compensation:

| Step | LotteryEntry | Checkout |
|---|---|---|
| Precondition | the entry is Won | the fan's own Checkout; holding, published and authorized while Held |
| Before the charge | nothing | `Checkout.Commit` |
| Capture cannot succeed | `LotteryEntry.RevertWin`, then `CardAuthorization.Release` | `Checkout.RevertCommit` |
| After the charge | `Order.Issue` | `Checkout.RecordCapture`, then `Order.Issue` |
| Then | announce `ORDER.paid` | announce `ORDER.paid` |

Rejected: a `CheckoutUseCase.Confirm` that commits and then starts `Issue`. A usecase does not call another usecase's method (the spec rule for `components/usecase`), and `Checkout.Commit` is an entity operation that `Issue` can call itself, as `IssueFromCheckout` does today.

### The fan's call waits for the workflow

`CheckoutHandler.Confirm` starts `Issue` with the workflow id `issue:checkout:<id>` and waits for its result for up to 30 seconds. A second Confirm for the same Checkout joins the same workflow (same id) and gets the same outcome, which replaces `Serialize` and its transaction held during the capture. When the 30 seconds pass, the handler returns Unavailable and the workflow goes on; the screen already maps Committed and Completed to "the purchase is being completed" (`route/checkout` "Outcome of placing the order").

### Retries

Capture and the steps after it use the same retry options as the lottery (`make-lottery-draw-durable` design "24-hour retries"). A Checkout charged but not issued when they end is reported with `LogKeyNeedsOperator`, which replaces the 10-minute report of `IssueDueCheckouts`.

### The completed-charge notice

`payment_intent.succeeded` is acknowledged without effect for every source. The capture is the synchronous response of the platform's own call, and `Issue` announces the Order. `processed_webhook_events` still records the notice, so a redelivery stays a no-op.

## Risks / Trade-offs

- [A Committed Checkout exists at the moment of the rollout, left by an interrupted old call] → Before the deploy, list Committed Checkouts read-only in prod; the product has no users, so none is expected. If one exists, finish it with the old code before deploying.
- [The 30-second wait holds a request goroutine and no database connection] → The wait polls the workflow handle; the workflow runs on the DBOS queue.

## Migration Plan

1. backend: `Issue` for a Checkout, the handler change, removal of `IssueFromCheckout`, `IssueDueCheckouts`, `FulfillPayment`, `Serialize` (its only caller goes) and the issuance part of the checkout sweeper.
2. Read-only prod check for Committed Checkouts, deploy, confirm the rollout, and buy one ticket with the Stripe Sandbox E2E.

Rollback: revert the backend release; Checkouts and Orders keep their shape.
