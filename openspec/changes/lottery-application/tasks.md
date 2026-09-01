## 0. Prerequisites (in flight in parallel — not code)

- [ ] 0.1 Stripe Connect account type + KYC/審査 application started (long-lead; needed for the live SetupIntent)
- [ ] 0.2 収納代行 counsel opinion in progress (#778) — does not block ④ spec/build, blocks live sale
- [ ] 0.3 Confirm ⑤ `ticket-purchase-and-issuance` handoff contract (win → off-session charge → issued | failed → 繰上げ) is agreed with whoever specs ⑤

## 1. Proto / entity (specification → BSR)

- [ ] 1.1 Define `LotterySalesPhase` (event ref, open_time, close_time, ticket capacity, max_tickets_per_application) on an organizer Event
- [ ] 1.2 Define `TicketApplication` (applicant/account, requested_ticket_count, 本人確認 name+contact, saved payment_method ref (pm_/customer), state: applied/won/lost/promoted/withdrawn/voided, payment_deadline) referencing ② Event
- [ ] 1.3 Persisted ordered waitlist (draw order) representation for losers
- [ ] 1.4 RPCs: organizer configure-lottery-phase; fan Apply / WithdrawApplication / GetMyApplication / GetResult; internal draw + 繰上げ
- [ ] 1.5 protovalidate (positive capacity, N ≤ max, window open<close, one-active-per-account invariants surfaced); buf lint/breaking; merge PR → Release → BSR gen

## 2. Backend — phase + application

- [ ] 2.1 Configure-lottery-phase (organizer-scoped; published-event precondition; validation)
- [ ] 2.2 Apply: window-open check, N ≤ max, 1-account/1-application, capture 本人確認, create SetupIntent (off_session, 3DS once, no hold), store token refs; no charge
- [ ] 2.3 WithdrawApplication before draw (+ allow re-apply while window open)

## 3. Backend — draw + outcomes

- [ ] 3.1 Draw job at window close (never before): uniform-random order + greedy fit (whole application, all-or-nothing), no oversell; persist winners + ordered loser waitlist
- [ ] 3.2 Mark winners with payment deadline; hand off each win to ⑤ for off-session charge (application state + signal, not ⑤ internals)
- [ ] 3.3 繰上げ: consume ⑤'s charge-failure/deadline-lapse signal → void win → promote next waitlisted application in draw order (no oversell); stop when waitlist empty
- [ ] 3.4 Results query (won/lost/promoted/withdrawn + deadline for winners)

## 4. Frontend (Aurelia PWA)

- [ ] 4.1 Apply flow: pick N ≤ max, 本人確認 capture, Stripe Elements card capture + SetupIntent confirm (no hold); confirmation-screen states charge-on-win timing (特商法)
- [ ] 4.2 My-application + result views (won/lost/promoted, payment deadline, 繰上げ status)
- [ ] 4.3 Withdraw application before draw

## 5. Organizer console

- [ ] 5.1 Configure a lottery phase on a published event (window, ticket capacity, max-per-application)
- [ ] 5.2 View phase status / draw outcome summary

## 6. Compliance / anti-scalp

- [ ] 6.1 1-account/1-application enforced at the application layer
- [ ] 6.2 本人確認 (name+contact) bound to account and carried to the ⑤ issuance handoff (covered-ticket precondition)
- [ ] 6.3 特商法 最終確認画面: charge-on-win timing/amount unambiguous, 総額表示 (ties to payments-design obligations table)

## 7. Release & verification

- [ ] 7.1 Cross-repo release order: spec → BSR → backend → frontend/console; provision any new draw job / consumer
- [ ] 7.2 End-to-end verify: configure phase → apply (SetupIntent, no charge) → close → draw (no oversell, groups intact, ordered waitlist) → win handoff → 繰上げ on simulated charge failure
- [ ] 7.3 Sync delta specs to main specs and archive the change
