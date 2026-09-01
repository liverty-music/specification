## 0. Prerequisites (long-lead — start in parallel, gate launch not spec)

- [ ] 0.1 Stripe Connect account type + KYC/審査 application; Connect onboarding for Organizers
- [ ] 0.2 収納代行 counsel opinion (#778 flag 1): discharge clause + hold-to-event escrow + no cross-border
- [ ] 0.3 適格請求書発行事業者 registration; 媒介者交付特例 stance
- [ ] 0.4 KOMOJU-vs-Stripe PoC outcome (confirm provider before locking the adapter)
- [ ] 0.5 Confirm the ④→⑤ handoff contract: **win captured (Stripe manual-capture at draw) → ⑤ Order + Ticket | capture failed → no Order** (no off-session charge / deadline / 繰上げ in ⑤); + the captured-payment ref + 本人確認/covered-ticket shape

## 1. Proto / entity (specification → BSR)

- [ ] 1.1 Define `Order` (provider, opaque pi_/pm_ of ④'s captured payment, status pending/paid/failed/refunded, amount+currency, paid_at, display facets) — never PAN/CVC
- [ ] 1.2 Define account-bound `Ticket` (buyer account, event ref, 本人確認 binding, covered-ticket face fields, order ref)
- [ ] 1.3 RPCs: internal create-Order-from-captured-payment + issuance; buyer GetOrder/GetMyTickets; admin refund/payout ops
- [ ] 1.4 protovalidate; buf lint/breaking; merge PR → Release → BSR gen

## 2. Backend — Order from ④'s captured payment (Stripe Connect)

- [ ] 2.1 On ④'s captured winning payment (destination charge + on_behalf_of + application_fee, JPY-only; the capture is ④'s), create the Order referencing that PaymentIntent — ⑤ runs NO separate off-session charge
- [ ] 2.2 Card-only context (④ enforces JPY/Amex-excluded at authorization)
- [ ] 2.3 Idempotent handling keyed on the capture/provider event id (redelivery-safe)
- [ ] 2.4 Failed capture → no Order, no issuance (surfaced for ④'s manual follow-up; no ⑤-side retry/繰上げ)

## 3. Backend — issuance (webhook-driven)

- [ ] 3.1 Webhook ingest: signature verification + idempotent handlers (capture/refund/dispute)
- [ ] 3.2 Issue N account-bound covered Tickets on confirmed capture only (never on client confirm); bind 本人確認
- [ ] 3.3 Set the buyer's ticket-journey to PAID on issuance (first-party authoritative)

## 4. Backend — payout & refunds

- [ ] 4.1 Manual-payout controller config; release after event + dispute buffer
- [ ] 4.2 Cancellation (中止) refund: face + system/発券 fee (keep processor fee) via Refund + transfer_reversal
- [ ] 4.3 Postponement (延期): no auto-refund; tickets stay valid for the new date
- [ ] 4.4 Chargeback/dispute ops: reserve past dispute window, representment evidence, transfer_reversal clawback

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
