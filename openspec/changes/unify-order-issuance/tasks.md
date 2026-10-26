## 1. Prerequisites

- [ ] 1.1 Confirm `make-lottery-draw-durable` is archived (so `components/usecase/order/issue` exists in the main specs) and released in backend; verify `openspec validate unify-order-issuance --strict` reports no archive refusal

## 2. Usecase (components/usecase/order/issue)

- [ ] 2.1 Extend `OrderUseCase.Issue` to take an `OrderSource` and run the Checkout steps of design "One workflow, two sources", reusing the retry options; verify one unit test per scenario passes with a fake `Flow`: "Fan places the order within the hold", "Hold lapsed before placing", "Concert cancelled during the checkout", "Card not yet authenticated", "Double tap on the action", "Someone else's checkout", "Checkout issued", "Card no longer chargeable", "Payment provider unavailable during capture", "Stopped after the charge", "Charged but never issued", "Verified sale issued", "IdentityVerification gone before confirm", "No requirement on a first-come sale", "Paid lottery win", "Paid checkout"
- [ ] 2.2 Remove `IssueFromCheckout`, `IssueDueCheckouts`, `FulfillPayment`, `CheckoutRepository.Serialize` and the issuance call in `startCheckoutSweepers` (keep `ReleaseExpired` and `RefundSold`), with their tests and mocks; verify `make check` passes with no reference left

## 3. Adapters (components/adapter/fan/api/rpc/checkout, components/adapter/fan/api/webhook/payment-events)

- [ ] 3.1 Change `CheckoutHandler.Confirm` to start `Issue` with the id `issue:checkout:<id>` and wait up to 30 seconds (design "The fan's call waits for the workflow"); verify the handler tests of "Checkout calls are for the signed-in fan" pass, including "Fan confirms" and a wait that ends in Unavailable
- [ ] 3.2 Acknowledge the completed-charge notice without effect; verify the webhook tests "Refund confirmation" and "Completed charge" pass and a redelivered notice stays a no-op

## 4. Screen and stories (components/infrastructure/fan/web/route/checkout, stories/buy-tickets-first-come, resell-a-ticket, attribute-a-purchase-to-a-referral-link)

- [ ] 4.1 Run the checkout with Playwright on a local build against the local backend and Stripe test mode: "Purchase placed" shows 2 tickets and 6,000円, and a payment provider stub that answers Unavailable for 60 seconds shows "Charge still completing" and then the tickets in the Tickets screen
- [ ] 4.2 Run the story integration tests of `buy-tickets-first-come` ("Two tickets bought"), `resell-a-ticket` ("One of two tickets resold") and `attribute-a-purchase-to-a-referral-link` against the new `Issue`; verify they pass, including one confirmation email per purchase

## 5. Release and production check

- [ ] 5.1 Read-only in prod before the deploy, list Committed Checkouts and record the count in design.md; stop if one exists (design "Risks")
- [ ] 5.2 Merge the backend PR, cut the release, confirm the fan-api rollout, and run `gh workflow run stripe-sandbox-e2e.yml` in backend; confirm the run succeeds

## 6. Archive

- [ ] 6.1 Edit the usecase diagrams (Purpose) of `stories/buy-tickets-first-come`, `stories/resell-a-ticket` and `stories/attribute-a-purchase-to-a-referral-link` to name `OrderUseCase.Issue` instead of `OrderUseCase.IssueFromCheckout`; delete the emptied `issue-from-checkout`, `issue-due-checkouts` and `fulfill-payment` specs; verify `openspec validate --specs` passes
