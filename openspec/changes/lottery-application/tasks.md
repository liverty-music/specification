## 0. Prerequisites (in flight in parallel — not code)

- [ ] 0.1 Stripe Connect account type + KYC/審査 application started (long-lead; needed for the live authorize + capture flow)
- [ ] 0.2 収納代行 counsel opinion in progress (#778) — incl. hold-vs-capture treatment; does not block ④ spec/build, blocks live sale
- [ ] 0.3 Confirm ⑤ `ticket-purchase-and-issuance` handoff contract (captured winning payment → Order + Ticket; ⑤ owns refund incl. post-capture issuance failure) is agreed with whoever specs ⑤

## 1. Proto / entity (specification → BSR)

> NOTE: the proto in PR #887 has been REVISED to the authorization-hold model
> (dropped `PaymentDeadlinePolicy` + `SetupIntent` RPC; `SavedPaymentMethod` →
> `PaymentAuthorization` (manual-capture PaymentIntent ref); states reduced to
> applied/won/lost/withdrawn; dropped 繰上げ RPC; added the 1–14-day window CEL and
> a `ticket_price` (JPY) on the phase). buf lint/format/breaking + openspec
> validate --strict pass locally.

- [x] 1.1 Define `LotterySalesPhase` (event ref, open_time, close_time with **duration 1–14 days**, ticket capacity, max_tickets_per_application, **ticket_price in JPY**) on an organizer Event — no payment-deadline policy
- [x] 1.2 Define `TicketApplication` (applicant/account, requested_ticket_count, 本人確認 name+contact, **payment-authorization ref (PaymentIntent, capture_method=manual)**, state: applied/won/lost/withdrawn) referencing ② Event
- [x] 1.3 Persisted ordered waitlist (random draw order) of losing applications for ⑦ resale
- [x] 1.4 RPCs: organizer configure-lottery-phase + view-status; fan Apply / WithdrawApplication / GetMyApplication / GetResult; internal draw job (capture winners / cancel losers) — no 繰上げ RPC
- [ ] 1.5 protovalidate (window duration 1–14 days, positive capacity, N ≤ max, open<close); buf lint/breaking; merge PR → Release → BSR gen — protovalidate + buf lint/format/breaking pass locally; merge PR → Release → BSR gen remain (CI-only)

## 2. Backend — phase + application

- [ ] 2.1 Configure-lottery-phase (organizer-scoped; published-event precondition; window 1–14 days + capacity/max validation) — usecase drafted locally; adjust to window bounds + drop deadline policy
- [ ] 2.2 Apply: window-open check, N ≤ max, 1-account/1-application, capture 本人確認, **authorize (hold) the ticket amount via Stripe manual-capture (JPY only, Amex rejected, 3DS once), store PaymentIntent ref; no capture** — usecase drafted locally against SetupIntent; rework to authorization hold
- [ ] 2.3 WithdrawApplication before draw → **release (cancel) the authorization**; allow re-apply while window open

## 3. Backend — draw + outcomes

- [ ] 3.1 Draw job at window close (never before): uniform-random order + greedy fit (whole application, all-or-nothing), no oversell; persist winners + ordered loser waitlist — CORE ALGORITHM done locally (`internal/entity/lottery_draw.go`, pure/injectable-rng, 100% cover, reusable as-is); job trigger + persistence remain (need BSR gen + Atlas migration)
- [ ] 3.2 At the draw: **capture winners / cancel losers**; hand each captured winner to ⑤ for Order + Ticket issuance; a capture failure leaves the seat unfilled + logged (no automatic 繰上げ)
- [ ] 3.3 Results query (won / lost / withdrawn)

> Dropped from MVP vs the prior plan: payment-deadline clock, charge-failure
> grace/re-auth, and automatic 繰上げ (the local `lottery_promotion.go` and
> `payment_deadline.go` are out of MVP scope; keep the loser waitlist only for ⑦).

## 4. Frontend (Aurelia PWA)

- [ ] 4.1 Apply flow: pick N ≤ max, 本人確認 capture, **Stripe card authorization (manual-capture, 3DS once, JPY only, Amex blocked at card entry)**; confirmation screen states authorize-at-apply / charge-on-win / release-on-loss timing (特商法)
- [ ] 4.2 My-application + result views (won / lost / withdrawn)
- [ ] 4.3 Withdraw application before draw (releases the hold)

## 5. Organizer console

- [ ] 5.1 Configure a lottery phase on a published event (window: **default 10 days, range 1–14 days**; ticket capacity; max-per-application)
- [ ] 5.2 View phase status / draw outcome summary

## 6. Compliance / anti-scalp

- [ ] 6.1 1-account/1-application enforced at the application layer
- [ ] 6.2 本人確認 (name+contact) bound to account and carried to the ⑤ issuance handoff (covered-ticket precondition)
- [ ] 6.3 特商法 最終確認画面: authorize-at-apply / charge-on-win (capture) / release-on-loss timing + amount unambiguous, 総額表示; accepted cards disclosed (JPY Visa/Mastercard/JCB/Diners/Discover; Amex not accepted)

## 7. Release & verification

- [ ] 7.1 Cross-repo release order: spec → BSR → backend → frontend/console; provision the draw job
- [ ] 7.2 End-to-end verify: configure phase → apply (authorize, no capture) → close → draw (no oversell, groups intact, ordered loser waitlist; **winners captured / losers released**) → ⑤ issuance handoff
- [ ] 7.3 Sync delta specs to main specs and archive the change
