## Why

A first-come purchase is issued by three paths that each own a part of the same flow. `OrderUseCase.IssueFromCheckout` runs from the fan's Confirm. The 1-minute `IssueDueCheckouts` sweeper finishes the purchase when that call stopped after the commit. `FulfillPayment` runs from the payment provider's completed-charge notice and is the only path that announces the Order as paid. After `make-lottery-draw-durable`, a won lottery entry is issued by one durable `OrderUseCase.Issue` that charges, issues and announces. This change moves the first-come checkout onto the same `Issue`, so an Order of either source is charged, issued and announced by one method that resumes on its own. The sweeper and the notice-driven issuance go. It also removes the remaining "Order without a Settlement" branches, which no Order can reach.

## What Changes

- New `OrderUseCase.Place` for the fan's Confirm. It checks synchronously what the fan can still fix: their own Checkout, holding, published, card authenticated for the amount, and IdentityVerification when the sale requires it. It then runs `Issue` for the Checkout and waits up to 30 seconds. After that it returns Unavailable and the purchase completes in the background, as the checkout screen already tells the fan.
- `OrderUseCase.Issue` takes a Checkout as its source too. It commits the tickets at the time the order was placed, charges once, gives the tickets back when the card can no longer be charged, and issues and announces the Order. An unreachable payment provider is tried again for up to 24 hours instead of waiting for the sweeper.
- **BREAKING** (internal API): `OrderUseCase.IssueFromCheckout` is replaced by `Place` and `Issue`. `CheckoutService.Confirm` keeps its name and request and now runs `Place`.
- `OrderUseCase.IssueDueCheckouts` and its 1-minute sweep are removed: a stopped `Issue` resumes on its own, and one that cannot finish is reported to an admin.
- `OrderUseCase.FulfillPayment` is removed. The completed-charge notice is acknowledged without effect.
- Every Order has a Settlement: `Refund`, `GetWithSettlement` and the admin `OrderService.Get` fail instead of treating a missing Settlement as normal, and the Settlement's ER diagram says one per Order.

## Capabilities

### New Capabilities

- `components/usecase/order/place`: checks and places a fan's order for their Checkout.

### Modified Capabilities

- `components/usecase/order/issue`: adds the Checkout source; the product-analytics signal names either source.
- `components/usecase/order/issue-from-checkout`, `issue-due-checkouts`, `fulfill-payment`: removed.
- `components/usecase/order/refund`, `get-with-settlement`, `components/adapter/admin/api/rpc/order`: a missing Settlement is a failure.
- `components/entity/settlement` (Purpose): `Order ||--|| Settlement`.
- `components/adapter/fan/api/webhook/payment-events`: a completed-charge notice is acknowledged without effect.
- `components/adapter/fan/api/rpc/checkout`, `components/infrastructure/fan/web/route/checkout`: placing the order runs `OrderUseCase.Place`.
- `stories/buy-tickets-first-come`, `stories/resell-a-ticket`, `stories/attribute-a-purchase-to-a-referral-link`: the fan places the order with `OrderUseCase.Place`; their usecase diagrams (Purpose) name it.

Unchanged and why: `components/entity/checkout/commit`, `revert-commit`, `record-capture` and `list-due` keep their contracts (`ListDue` is still read by `CheckoutUseCase.ReleaseExpired`); `components/entity/order/issue` already makes the Checkout Completed in the same step; `components/entity/order/commit-refund` still takes no Settlement for one already Reversed by resales; `components/usecase/checkout/release-expired` still gives back the card authorization of a Checkout that was never committed.

## Impact

- **backend**: `Place`; `Issue` gains the Checkout source and the `checkout` queue; `IssueFromCheckout`, `IssueDueCheckouts`, `FulfillPayment`, `Serialize` and the issuance part of the checkout sweeper go; `CheckoutHandler.Confirm` calls `Place`; the Settlement reads fail on a missing Settlement.
- **frontend**: none beyond the spec's wording; the Confirm request and response do not change.
- **Depends on**: `make-lottery-draw-durable` (and through it `introduce-durable-workflows`) archived first, so `components/usecase/order/issue` exists in the main specs.
