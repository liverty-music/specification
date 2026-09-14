## 0. Prerequisites (long-lead — start in parallel, gate launch not spec)

- [ ] 0.1 収納代行 counsel opinion (#778 flag 1): discharge clause + hold-to-event escrow + no cross-border (Stripe Connect onboarding itself is owned by `ticket-settlement-and-payout`)
- [ ] 0.2 適格請求書発行事業者 registration; 媒介者交付特例 stance
- [ ] 0.3 KOMOJU-vs-Stripe PoC outcome (confirm provider before locking the adapter)
- [ ] 0.4 Confirm the ④→⑤ handoff contract: **win captured (Stripe manual-capture at draw) → ⑤ Order + Ticket | capture failed → no Order** (no off-session charge / deadline / 繰上げ in ⑤); + the captured-payment ref + 本人確認/covered-ticket shape

## 1. Proto / entity (specification → BSR)

- [x] 1.1 Define `Order` (provider, opaque pi_/pm_ of ④'s captured payment, status paid→refunded/failed — **no pending**, amount+currency, paid_at, display facets) — never PAN/CVC
- [x] 1.2 Define account-bound `Ticket` (buyer account, event ref, 本人確認 binding, covered-ticket face fields, order ref)
- [x] 1.3 RPCs: internal create-Order-from-captured-payment + issuance; buyer GetOrder/GetMyTickets; admin refund/payout ops
- [ ] 1.4 protovalidate; buf lint/breaking; merge PR → Release → BSR gen (protovalidate + buf lint/breaking PASS locally; PR merge → Release → BSR gen still pending)

## 2. Backend — Order from ④'s captured payment

- [ ] 2.1 On ④'s captured winning payment (a plain platform-account charge by ④; funds already platform-held; JPY-only), create the Order referencing that PaymentIntent — ⑤ runs NO separate off-session charge
- [ ] 2.2 Card-only context (④ enforces JPY/Amex-excluded at authorization)
- [ ] 2.3 Idempotent handling keyed on the capture/provider event id (redelivery-safe)
- [ ] 2.4 Failed capture → no Order, no issuance (surfaced for ④'s manual follow-up; no ⑤-side retry/繰上げ)

## 3. Backend — issuance (Won-captured-driven)

- [ ] 3.1 Issuance idempotency keyed on ④'s Won-captured signal (redelivery-safe; no double-Order/double-issue). Refund/dispute webhook ingest belongs to `ticket-settlement-and-payout`.
- [ ] 3.2 Issue N account-bound covered Tickets on the captured-win signal only (never on client confirm); bind 本人確認
- [ ] 3.3 Set the buyer's ticket-journey to PAID on issuance (first-party authoritative)

## 4. Refund policy (execution owned by ticket-settlement-and-payout)

- [x] 4.1 Define the refund **policy** ⑤ owns: cancellation (中止) → refund current holder (face + system/発券 fee, keep processor fee); postponement (延期) → no auto-refund + holder-initiated window; issuance-failure → refund. The `Refund` + `transfer_reversal` execution + reserve/chargeback ops live in `ticket-settlement-and-payout`.
      [Implemented via OrderAdminService.RefundOrder handler + RefundOrderUseCase. CAVEAT: the postponement holder-initiated window is NOT time-enforced in code — no reschedule/announcement timestamp is modeled; the admin call is authoritative. See 4.2 follow-up + design "Window-start caveat".]
- [ ] 4.2 **Follow-up: model the postponement window-start.** Add a **server-owned** reschedule/announcement timestamp to the **Event entity** (stamped when the organizer reschedules, independent of the refund caller) so the holder-initiated window can be time-gated correctly. (A window-start on `RefundOrderRequest` is NOT sufficient — the same admin caller the window constrains would supply it.) Proto/spec change; until then the window is admin-authoritative (not code-enforced). Also fold in the processor-fee retention math (currently full-amount refund + TODO).

## 5. Frontend (Aurelia PWA)

- [ ] 5.1 Order/payment result + issued-ticket confirmation surfaces (checkout card capture lives in ④'s apply)
- [ ] 5.2 Refund/cancellation status surfacing

## 6. Compliance (payments-design obligations table)

- [ ] 6.1 総額表示 (税込 lines + grand total) on all consumer-facing prices
- [ ] 6.2 特商法 最終確認画面 + 返品特約 (no returns except cancellation/postponement) + per-Organizer 事業者情報
- [ ] 6.3 PCI SAQ A (Stripe Elements, no PAN); EMV 3DS on file
- [ ] 6.4 個人情報 越境移転 (Stripe US 委託) privacy disclosure + DPA; 電子帳簿保存法 record retention; 領収書/適格請求書 (クレカ決済表記, 登録番号)

## 7. Release & verification

- [ ] 7.1 Cross-repo release order: spec → BSR → backend → frontend/console; provision webhook + charge/payout jobs
- [ ] 7.2 End-to-end verify (Stripe test): ④ captures winner → webhook → ⑤ Order + issue N covered tickets → ticket-journey PAID; failed capture → no Order; cancellation refund; postponement keeps valid; duplicate-webhook idempotency
- [ ] 7.3 Sync delta specs to main specs and archive the change
