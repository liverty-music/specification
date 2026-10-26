## Why

A first-come purchase is issued by three paths that each own a part of the same flow: `OrderUseCase.IssueFromCheckout` from the fan's Confirm, the 1-minute `IssueDueCheckouts` sweeper when that call stopped after the commit, and `FulfillPayment` from the payment provider's completed-charge notice, which is the only path that announces the Order as paid. After `make-lottery-draw-durable`, a won lottery entry is issued by one durable `OrderUseCase.Issue` that charges, issues and announces. This change moves the first-come checkout onto the same `Issue`, so an Order of either source is charged, issued and announced by one method that resumes on its own, and the sweeper and the notice-driven issuance go.

## What Changes

- `OrderUseCase.Issue` takes a Checkout as its source too. For a Checkout it keeps today's rules: the fan's own Checkout, committed while it is holding, charged once, the tickets given back when the card can no longer be charged, and the Order, its Tickets and its Settlement issued and announced as paid. A capture that fails because the payment provider cannot be reached is tried again for up to 24 hours instead of waiting for the sweeper; the fan's call returns Unavailable after 30 seconds and the purchase completes in the background, as the checkout screen already tells the fan.
- **BREAKING** (internal API): `OrderUseCase.IssueFromCheckout` is replaced by `OrderUseCase.Issue`. `CheckoutService.Confirm` keeps its name and request and now runs `Issue`.
- `OrderUseCase.IssueDueCheckouts` and its 1-minute sweeper are removed: a stopped `Issue` resumes on its own, and a charged Checkout that stays unissued is reported to an admin when the retries end.
- `OrderUseCase.FulfillPayment` is removed. The completed-charge notice is acknowledged without effect, because `Issue` already announced the Order.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/usecase/order/issue`: adds the Checkout source; the product-analytics signal names either source.
- `components/usecase/order/issue-from-checkout`: removed, replaced by `issue`.
- `components/usecase/order/issue-due-checkouts`: removed.
- `components/usecase/order/fulfill-payment`: removed.
- `components/adapter/fan/api/webhook/payment-events`: a completed-charge notice is acknowledged without effect.
- `components/adapter/fan/api/rpc/checkout`: Confirm runs `OrderUseCase.Issue`.
- `components/infrastructure/fan/web/route/checkout`: placing the order calls `OrderUseCase.Issue`.
- `stories/buy-tickets-first-come`, `stories/resell-a-ticket`, `stories/attribute-a-purchase-to-a-referral-link`: the fan places the order with `OrderUseCase.Issue`; their usecase diagrams (Purpose) name it.

Unchanged and why: `components/entity/checkout/commit`, `revert-commit`, `record-capture` and `list-due` keep their contracts (`ListDue` is still read by `CheckoutUseCase.ReleaseExpired`); `components/entity/order/issue` already makes the Checkout Completed in the same step; `components/usecase/checkout/release-expired` still gives back the card authorization of a Checkout that was never committed.

## Impact

- **backend**: `OrderUseCase.Issue` gains the Checkout source; `IssueFromCheckout`, `IssueDueCheckouts`, `FulfillPayment` and the issuance part of the checkout sweeper goroutine go; `CheckoutHandler.Confirm` waits for the workflow's result for up to 30 seconds.
- **frontend**: none beyond the spec's wording; the Confirm request and response do not change.
- **Depends on**: `make-lottery-draw-durable` (the DBOS runtime and `OrderUseCase.Issue`) is archived first.
