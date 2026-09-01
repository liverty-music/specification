## 0. Prerequisites (long-lead — start in parallel, gate launch not spec)

- [ ] 0.1 Stripe Connect account type + KYC/審査 application; Connect onboarding for Organizers
- [ ] 0.2 収納代行 counsel opinion (#778 flag 1): discharge clause + hold-to-event escrow + no cross-border
- [ ] 0.3 適格請求書発行事業者 registration; 媒介者交付特例 stance
- [ ] 0.4 KOMOJU-vs-Stripe PoC outcome (confirm provider before locking the adapter)
- [ ] 0.5 Confirm the ④ handoff contract (win → charge → issued | failed → 繰上げ) and the saved-pm/本人確認 shape

## 1. Proto / entity (specification → BSR)

- [ ] 1.1 Define `Order` (provider, opaque pi_/pm_, status pending/paid/failed/refunded, amount+currency, paid_at, display facets) — never PAN/CVC
- [ ] 1.2 Define account-bound `Ticket` (buyer account, event ref, 本人確認 binding, covered-ticket face fields, order ref)
- [ ] 1.3 RPCs: internal charge-on-win + issuance; buyer GetOrder/GetMyTickets; admin refund/payout ops
- [ ] 1.4 protovalidate; buf lint/breaking; merge PR → Release → BSR gen

## 2. Backend — charge (Stripe Connect)

- [ ] 2.1 Off-session charge adapter: destination charge + on_behalf_of + application_fee, MIT (no CVC), using ④'s saved pm
- [ ] 2.2 Card-only guard (debit/prepaid/wallet ok; konbini/PayPay excluded)
- [ ] 2.3 Batch charge at draw close with per-Order idempotency keys + provider rate-limit + safe retries
- [ ] 2.4 Charge-failure/deadline-lapse → mark Order failed + emit ④ 繰上げ signal (no issuance)

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
- [ ] 7.2 End-to-end verify (Stripe test): win → off-session charge → webhook → issue N covered tickets → ticket-journey PAID; failure → 繰上げ; cancellation refund; postponement keeps valid; duplicate-webhook idempotency
- [ ] 7.3 Sync delta specs to main specs and archive the change
