## 0. Prerequisites (long-lead — start in parallel, gate launch not spec)

- [ ] 0.1 収納代行 counsel opinion (#778 flag 1): discharge clause + hold-to-event escrow + no cross-border (Stripe Connect onboarding itself is owned by `ticket-settlement-and-payout`)
- [ ] 0.2 適格請求書発行事業者 registration; 媒介者交付特例 stance
- [x] 0.4 Confirm the ④→⑤ handoff contract: **win captured (Stripe manual-capture at draw) → ⑤ Order + Ticket | capture failed → no Order** (no off-session charge / deadline / 繰上げ in ⑤); + the captured-payment ref + 本人確認/covered-ticket shape (locked in delta spec + design; implemented be #445 IssueFromCapturedWin — not-Won → FailedPrecondition/no Order, GetCapturedPayment reads pi.AmountReceived/currency/card facets)

## 1. Proto / entity (specification → BSR)

- [x] 1.1 Define `Order` (provider, opaque pi_/pm_ of ④'s captured payment, status paid→refunded/failed — **no pending**, amount+currency, paid_at, display facets) — never PAN/CVC
- [x] 1.2 Define account-bound `Ticket` (buyer account, event ref, 本人確認 binding, covered-ticket face fields, order ref)
- [x] 1.3 RPCs: internal create-Order-from-captured-payment + issuance; buyer GetOrder/GetMyTickets; admin refund/payout ops
- [x] 1.4 protovalidate; buf lint/breaking; merge PR → Release → BSR gen (spec #938 merged → Release v0.62.0 → BSR gen succeeded)

## 2. Backend — Order from ④'s captured payment

- [x] 2.1 On ④'s captured winning payment (a plain platform-account charge by ④; funds already platform-held; JPY-only), create the Order referencing that PaymentIntent — ⑤ runs NO separate off-session charge (be #445: IssuanceUseCase.IssueFromCapturedWin)
- [x] 2.2 Card-only context (④ enforces JPY/Amex-excluded at authorization) (⑤ consumes ④'s captured card payment; enforcement shipped in ④)
- [x] 2.3 Idempotent handling keyed on the capture/provider event id (redelivery-safe) (be #445: one Order per application via unique index → AlreadyExists re-read)
- [x] 2.4 Failed capture → no Order, no issuance (surfaced for ④'s manual follow-up; no ⑤-side retry/繰上げ) (be #445: not-Won guard → FailedPrecondition, no Order)

## 3. Backend — issuance (Won-captured-driven)

- [x] 3.1 Issuance idempotency keyed on ④'s Won-captured signal (redelivery-safe; no double-Order/double-issue). Refund/dispute webhook ingest belongs to `ticket-settlement-and-payout`. (be #445: sweeper + idempotent IssueFromCapturedWin)
- [x] 3.2 Issue N account-bound covered Tickets on the captured-win signal only (never on client confirm); bind 本人確認 (be #445: transactional Issue; verified-identity bound when phase required it)
- [x] 3.3 Set the buyer's ticket-journey to PAID on issuance (first-party authoritative) (be #445)

## 4. Refund policy (execution owned by ticket-settlement-and-payout)

- [x] 4.1 Define the refund **policy** ⑤ owns: cancellation (中止) → refund current holder (face + system/発券 fee, keep processor fee); postponement (延期) → no auto-refund + holder-initiated window; issuance-failure → refund. The `Refund` + `transfer_reversal` execution + reserve/chargeback ops live in `ticket-settlement-and-payout`.
      [Implemented via OrderAdminService.RefundOrder handler + RefundOrderUseCase. CAVEAT: the postponement holder-initiated window is NOT time-enforced in code — no reschedule/announcement timestamp is modeled; the admin call is authoritative. See 4.2 follow-up + design "Window-start caveat".]
- [x] 4.2 **Follow-up: model the postponement window-start.** Add a **server-owned** reschedule/announcement timestamp to the **Event entity** (stamped when the organizer reschedules, independent of the refund caller) so the holder-initiated window can be time-gated correctly. (A window-start on `RefundOrderRequest` is NOT sufficient — the same admin caller the window constrains would supply it.)
      [Proto `Event.rescheduled_time` (spec #949, v0.64.0/BSR). Backend gate (be #451): `RefundOrderUseCase` reads `events.rescheduled_at` via an orders→tickets→events lookup and rejects `POSTPONEMENT_WINDOW` refunds past `rescheduled_at + PostponementRefundWindow` (14d MVP default, tunable); when `rescheduled_at` is NULL it falls back to admin-authoritative (logged). Processor-fee retention math intentionally UNCHANGED — the full `Order.Amount` refund already makes the buyer whole (face + system/発券 fee) with the processor fee retained by Stripe not returning it; a precise per-fee subtraction is deferred to the fee-model decision (would otherwise short the buyer). REMAINING (out of ⑤ scope): the organizer **reschedule flow** that actually stamps `rescheduled_at` lives in `organizer-event-authoring`; until it ships the gate always falls back. The 14-day window duration is an open policy value.]

## 5. Frontend (Aurelia PWA)

- [x] 5.1 Order/payment result + issued-ticket confirmation surfaces (checkout card capture lives in ④'s apply) (fe #608 My Tickets + #609 Order detail)
- [x] 5.2 Refund/cancellation status surfacing (fe #609/#610: Order detail 返金済み/失敗 banner + voided tickets)

## 6. Compliance (payments-design obligations table)

- [ ] 6.1 総額表示 (税込 lines + grand total) on all consumer-facing prices
- [ ] 6.2 特商法 最終確認画面 + 返品特約 (no returns except cancellation/postponement) + per-Organizer 事業者情報
- [ ] 6.3 PCI SAQ A (Stripe Elements, no PAN); EMV 3DS on file
- [ ] 6.4 個人情報 越境移転 (Stripe US 委託) privacy disclosure + DPA; 電子帳簿保存法 record retention; 領収書/適格請求書 (クレカ決済表記, 登録番号)

## 7. Release & verification

- [ ] 7.1 Cross-repo release order: spec → BSR → backend → frontend/console; provision webhook + charge/payout jobs
- [ ] 7.2 End-to-end verify (Stripe test): ④ captures winner → webhook → ⑤ Order + issue N covered tickets → ticket-journey PAID; failed capture → no Order; cancellation refund; postponement keeps valid; duplicate-webhook idempotency
- [ ] 7.3 Sync delta specs to main specs and archive the change
