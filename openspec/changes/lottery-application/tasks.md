## 0. Prerequisites (in flight in parallel — not code)

- [ ] 0.1 Stripe Connect account type + KYC/審査 application started (long-lead; needed for the live authorize + capture flow)
- [ ] 0.2 収納代行 counsel opinion in progress (#778) — incl. hold-vs-capture treatment; does not block ④ spec/build, blocks live sale
- [ ] 0.3 Confirm ⑤ `ticket-purchase-and-issuance` handoff contract (captured winning payment → Order + Ticket; ⑤ owns refund incl. post-capture issuance failure) is agreed with whoever specs ⑤ — ⑤'s change docs on main are already reconciled to this authorization-hold contract (no ⑤-side off-session charge / SetupIntent / deadline / 繰上げ); only human sign-off with the ⑤ owner remains

## 1. Proto / entity (specification → BSR)

> NOTE: the proto (PR #887) shipped the authorization-hold model
> (dropped `PaymentDeadlinePolicy` + `SetupIntent` RPC; `SavedPaymentMethod` →
> `PaymentAuthorization` (manual-capture PaymentIntent ref); states reduced to
> applied/won/lost/withdrawn; dropped 繰上げ RPC; added the 1–14-day window CEL and
> a `ticket_price` (JPY) on the phase). Merged → **Release v0.58.0** → BSR gen
> published; backend/frontend consume the generated types.

- [x] 1.1 Define `LotterySalesPhase` (event ref, open_time, close_time with **duration 1–14 days**, ticket capacity, max_tickets_per_application, **ticket_price in JPY**) on an organizer Event — no payment-deadline policy
- [x] 1.2 Define `TicketApplication` (applicant/account, requested_ticket_count, 本人確認 name+contact, **payment-authorization ref (PaymentIntent, capture_method=manual)**, state: applied/won/lost/withdrawn) referencing ② Event
- [x] 1.3 Persisted ordered waitlist (random draw order) of losing applications for ⑦ resale
- [x] 1.4 RPCs: organizer configure-lottery-phase + view-status; fan Apply / WithdrawApplication / GetMyApplication / GetResult; internal draw job (capture winners / cancel losers) — no 繰上げ RPC
- [x] 1.5 protovalidate (window duration 1–14 days, positive capacity, N ≤ max, open<close); buf lint/breaking; merge PR #887 → **Release v0.58.0** → BSR gen — DONE (published; downstream deps upgraded)

## 2. Backend — phase + application

> Shipped in backend PR #426 (`feat(lottery): implement ④ lottery-application
> backend (apply + draw + capture)`), merged to backend/main.

- [x] 2.1 Configure-lottery-phase (organizer-scoped; published-event precondition; window 1–14 days + capacity/max validation) — `lottery_uc.go` Configure + `lottery_phase_repo.go`; window-bounds validation, no deadline policy
- [x] 2.2 Apply: window-open check, N ≤ max, 1-account/1-application, capture 本人確認, **authorize (hold) the ticket amount via Stripe manual-capture (JPY only, Amex rejected, 3DS once), store PaymentIntent ref; no capture** — `lottery_uc.go` Apply + `stripe_authorization.go` (`capture_method=manual`); reworked from the earlier SetupIntent draft to the authorization hold
- [x] 2.3 WithdrawApplication before draw → **release (cancel) the authorization**; allow re-apply while window open — `lottery_uc.go` Withdraw; partial-unique active-index permits re-apply

## 3. Backend — draw + outcomes

> Shipped in backend PR #426.

- [x] 3.1 Draw job at window close (never before): uniform-random order + greedy fit (whole application, all-or-nothing), no oversell; persist winners + ordered loser waitlist — `internal/entity/lottery_draw.go` (pure/injectable-rng, 100% cover, defensive oversell guard, statistical fairness test) + `di/lottery_draw_job.go` 1-min in-process sweeper + `drawn_at` idempotency + transactional `PersistDrawOutcome` + Atlas migration `20260902010000_add_lottery_tables.sql`
- [x] 3.2 At the draw: **capture winners / cancel losers**; hand each captured winner to ⑤ for Order + Ticket issuance; a capture failure leaves the seat unfilled + logged (no automatic 繰上げ) — `lottery_uc.go` RunDraw via `PaymentAuthorizationPort`; Won state is the ⑤ handoff signal (⑤ consumes Won rows)
- [x] 3.3 Results query (won / lost / withdrawn) — `lottery_uc.go` GetMyApplication / GetResult / GetLotteryPhaseStatus + handlers

> Dropped from MVP vs the prior plan: payment-deadline clock, charge-failure
> grace/re-auth, and automatic 繰上げ (removed from scope; keep the loser waitlist
> only for ⑦).

## 4. Frontend (Aurelia PWA)

> Shipped in frontend PR #577 (`feat(lottery): ④ fan apply/result/withdraw +
> organizer console`), merged to frontend/main.

- [x] 4.1 Apply flow: pick N ≤ max, 本人確認 capture, **Stripe card authorization (manual-capture, 3DS once, JPY only, Amex blocked at card entry)**; confirmation screen states authorize-at-apply / charge-on-win / release-on-loss timing (特商法) — `src/routes/lottery-apply/*` + `lottery-client.ts` + `stripe-service.ts` (`@stripe/stripe-js/pure`, asserts `requires_capture`); unit-tested. Visual verify in-browser pending (7.2 — needs Stripe test key + reachable env)
- [x] 4.2 My-application + result views (won / lost / withdrawn) — `src/routes/lottery-application/*`, state labels + pre-draw + loading/empty/error, unit-tested
- [x] 4.3 Withdraw application before draw (releases the hold) — Applied-only withdraw action + confirm step + FAILED_PRECONDITION handling, tested

## 5. Organizer console

> Shipped in frontend PR #577.

- [x] 5.1 Configure a lottery phase on a published event (window: **default 10 days, range 1–14 days**; ticket capacity; max-per-application) — `organizer/lottery-phase-editor/*` + `services/lottery-phase-client.ts`, org-scoped transport, validation; entry-point deep-link deferred (dashboard exposes no event ids yet)
- [x] 5.2 View phase status / draw outcome summary — `organizer/lottery-status/*`, window state + draw-completed + pre/post-draw tallies, tested

## 6. Compliance / anti-scalp

> Shipped across backend PR #426 + frontend PR #577.

- [x] 6.1 1-account/1-application enforced at the application layer — partial unique index `uq_ticket_applications_active` (state IN applied/won/lost, excludes withdrawn) + usecase guard
- [x] 6.2 本人確認 (name+contact) bound to account and carried to the ⑤ issuance handoff (covered-ticket precondition) — `ApplicantIdentity` on `TicketApplication`, persisted and surfaced on Won rows for ⑤
- [x] 6.3 特商法 最終確認画面: authorize-at-apply / charge-on-win (capture) / release-on-loss timing + amount unambiguous, 総額表示; accepted cards disclosed (JPY Visa/Mastercard/JCB/Diners/Discover; Amex not accepted) — `lottery-apply` confirmation screen + `formatJpy`

## 7. Release & verification

- [x] 7.1 Cross-repo release order: spec → BSR → backend → frontend/console; provision the draw job — spec **v0.58.0** released → BSR gen → backend **#426** merged (in-process draw sweeper, no extra provisioning) → frontend **#577** merged
- [ ] 7.2 End-to-end verify: configure phase → apply (authorize, no capture) → close → draw (no oversell, groups intact, ordered loser waitlist; **winners captured / losers released**) → ⑤ issuance handoff — BLOCKED: needs a Stripe test/sandbox account (0.1) + a reachable environment (dev is intentionally stopped); unit/integration tests pass, browser/E2E verify pending
- [ ] 7.3 Sync delta specs to main specs and archive the change — gated on 7.2 (verify-before-archive) + 0.x external prerequisites
