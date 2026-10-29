## 1. Prerequisites

- [ ] 1.1 Confirm `remodel-ticket-sales` and then `make-lottery-draw-durable` are archived (so `components/usecase/order/issue` and the remodeled Checkout and Order specs are in the main specs) and released in backend; verify `openspec validate unify-order-issuance --strict` passes with no archive refusal

## 2. Usecases (components/usecase/order/place, issue, refund, get-with-settlement)

- [ ] 2.1 Extend `OrderUseCase.Issue` to take an `OrderSource` and run the Checkout steps of design "One workflow, two sources" on the `checkout` queue (global concurrency 2); verify one unit test per scenario passes with mocked `Flow` and operations: "Placed checkout", "Checkout issued", "Hold already over", "Card no longer chargeable", "Payment provider unavailable during capture", "Charged but never issued", "Verified sale issued", "No requirement on a first-come sale", "Paid lottery win", "Paid checkout"
- [ ] 2.2 Add `OrderUseCase.Place` (design "Check before the workflow, commit inside it"); verify one unit test per scenario passes with mocked `Workflows`: "Fan places the order within the hold", "Hold lapsed before placing", "Checkout already expired", "Concert cancelled during the checkout", "Card not yet authenticated", "IdentityVerification gone before placing", "Double tap on the action", "Someone else's checkout", "Card no longer chargeable", "Charge still completing"
- [ ] 2.3 Make a Paid Order's missing Settlement a failure in `Refund` and `GetWithSettlement`, and return a never-paid Order alone without reading a Settlement; verify the unit tests "Payout already released", "Payout not yet released", "Settlement given up by resales", "Settlement unreadable", "Order with a held settlement", "Order with no settlement yet", "Order not found", "Settlement missing" pass
- [ ] 2.4 Remove `IssueFromCheckout`, `IssueDueCheckouts`, `FulfillPayment`, `CheckoutRepository.Serialize` and the issuance call in the checkout sweeper (keep `ReleaseExpired`), with their tests and mocks; verify `make check` passes with no reference left

## 3. Adapters (components/adapter/fan/api/rpc/checkout, components/adapter/fan/api/webhook/payment-events, components/adapter/admin/api/rpc/order)

- [ ] 3.1 Change `CheckoutHandler.Confirm` to call `OrderUseCase.Place`; verify the handler tests of "Checkout calls are for the signed-in fan" pass, including "Fan confirms"
- [ ] 3.2 Acknowledge the completed-charge notice without effect; verify the webhook tests "Refund confirmation" and "Completed charge" pass and a redelivered notice stays a no-op
- [ ] 3.3 The admin `OrderService.Get` returns a never-paid Order alone and fails for a Paid Order without its Settlement; verify the handler tests of "Admins read an order with its settlement" pass, including "Order without a settlement" and "Paid order without its settlement"

## 4. Screen and stories (components/infrastructure/fan/web/route/checkout, stories/buy-tickets-first-come, attribute-a-purchase-to-a-referral-link)

- [ ] 4.1 Run the checkout with Playwright on a local build against the local backend and Stripe test mode: "Purchase placed" shows 2 tickets and 6,000円, and a payment provider stub that answers Unavailable for 60 seconds shows "Charge still completing" and then the tickets in the Tickets screen
- [ ] 4.2 Run the story integration tests of `buy-tickets-first-come` ("Two tickets bought") and `attribute-a-purchase-to-a-referral-link` against `Place` and `Issue` with the worker running; verify they pass, including one confirmation email per purchase

## 5. Release and production check

- [ ] 5.1 Read-only in prod before the deploy, list Committed Checkouts and Paid Orders without a Settlement, and record the counts in design.md; stop if either exists (design "Risks")
- [ ] 5.2 Merge the backend PR, cut the release, confirm the fan-api and workflow-worker rollouts, and run `gh workflow run stripe-sandbox-e2e.yml` in backend; confirm the run succeeds

## 6. Archive

- [ ] 6.1 Delete the emptied `issue-from-checkout`, `issue-due-checkouts` and `fulfill-payment` specs; verify `openspec validate --specs` passes
- [ ] 6.2 Remove `OrderUseCase.IssueFromCheckout` from the usecase diagrams of `stories/buy-tickets-first-come` and `attribute-a-purchase-to-a-referral-link` (kept until the story text stops naming it); verify `python3 scripts/check-story-diagrams.py` passes
