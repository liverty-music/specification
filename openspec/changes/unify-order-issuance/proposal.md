## Why

A first-come purchase is issued by three paths that each own a part of the same flow. `OrderUseCase.IssueFromCheckout` runs from the fan's Confirm. The 1-minute `IssueDueCheckouts` sweeper finishes the purchase when that call stopped after the commit. `FulfillPayment` runs from the payment provider's completed-charge notice and is the only path that announces a checkout's Order as paid. After `make-lottery-draw-durable`, a won lottery entry's Pending Order is made Paid by one durable `OrderUseCase.Issue` that charges, issues and announces. This change moves the first-come checkout onto the same `Issue`, so the Pending Order of either source is charged, issued and announced by one method that resumes on its own. The sweeper and the notice-driven issuance go. It also makes a missing Settlement of a Paid Order a failure, since `Order.Issue` always stores the two together.

## What Changes

- New `OrderUseCase.Place` for the fan's Confirm. It checks synchronously what the fan can still fix: their own Checkout, holding, the event published, the Order's card authorization authenticated for its amount, and an IdentityVerification when the sale requires it. It then runs `Issue` for the Checkout and waits up to 30 seconds. After that it returns Unavailable and the purchase completes in the background, as the checkout screen already tells the fan.
- `OrderUseCase.Issue` takes a Checkout as its source too. It commits the tickets at the time the commit runs (never backdated, so a lapsed hold cannot oversell), charges once, makes the Pending Order Paid with its Tickets and Settlement, and announces it. When the card can no longer be charged it gives the tickets back with `Checkout.RevertCommit`, which makes the Order Void. An unreachable payment provider is tried again for up to 24 hours instead of waiting for the sweeper.
- **BREAKING** (internal API): `OrderUseCase.IssueFromCheckout` is replaced by `Place` and `Issue`. `CheckoutService.Confirm` keeps its name and request and now runs `Place`.
- `OrderUseCase.IssueDueCheckouts` and its 1-minute sweep are removed: a stopped `Issue` resumes on its own, and one that cannot finish is reported to an admin.
- `OrderUseCase.FulfillPayment` is removed. The completed-charge notice is acknowledged without effect.
- A Paid or Refunded Order always has a Settlement: `Refund` fails instead of clawing back nothing when it is missing, and `GetWithSettlement` and the admin `OrderService.Get` return the Order alone only for an Order that was never paid (Pending or Void).
- Resale purchases are not part of this change: official resale is no longer bought through a Checkout (`remodel-ticket-sales`, `resell-tickets-by-lottery`).

## Capabilities

### New Capabilities

- `components/usecase/order/place`: checks and places a fan's order for their Checkout.

### Modified Capabilities

- `components/usecase/order/issue`: adds the Checkout source; the product-analytics signal names either source.
- `components/usecase/order/issue-from-checkout`, `components/usecase/order/issue-due-checkouts`, `components/usecase/order/fulfill-payment`: removed.
- `components/usecase/order/refund`, `components/usecase/order/get-with-settlement`, `components/adapter/admin/api/rpc/order`: a Paid Order's missing Settlement is a failure.
- `components/adapter/fan/api/webhook/payment-events`: a completed-charge notice is acknowledged without effect.
- `components/adapter/fan/api/rpc/checkout`, `components/infrastructure/fan/web/route/checkout`: placing the order runs `OrderUseCase.Place`.
- `stories/buy-tickets-first-come`, `stories/attribute-a-purchase-to-a-referral-link`: the fan places the order with `OrderUseCase.Place`; their usecase diagrams (Purpose, edited in the main specs) name it.
- `components/entity/settlement` (Purpose, edited in the main spec): a Paid Order has exactly one Settlement.

Unchanged and why: `components/entity/checkout/commit`, `revert-commit`, `record-capture` and `list-due` keep their contracts as `remodel-ticket-sales` leaves them (`ListDue` is still read by `CheckoutUseCase.ReleaseExpired`); `components/entity/order/issue` already makes the Pending Order Paid and the Checkout Completed in the same step; `components/usecase/checkout/release-expired` still gives back the card authorization of a Checkout that was never committed.

## Impact

- **backend**: `Place`; `Issue` gains the Checkout source and the `checkout` queue; `IssueFromCheckout`, `IssueDueCheckouts`, `FulfillPayment`, `CheckoutRepository.Serialize` and the issuance part of the checkout sweeper go; `CheckoutHandler.Confirm` calls `Place`; the Settlement reads fail on a Paid Order without one.
- **frontend**: none beyond the spec's wording; the Confirm request and response do not change.
- **Depends on**, archived in this order before this change: `remodel-ticket-sales` (Pending Orders, Checkout only for a FirstCome sale's stock), then `make-lottery-draw-durable` (and through it the archived `introduce-durable-workflows`), which creates `components/usecase/order/issue`. The deltas here are written against the main specs as they are after both.
