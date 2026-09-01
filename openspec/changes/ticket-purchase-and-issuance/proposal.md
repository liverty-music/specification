## Why

Phase 3 step ⑤. ④ `lottery-application` produces **winners** (a right to be
charged, with a saved card) but no money moves and no ticket exists. This change
is the **money + issuance pipeline**: charge the winner off-session, record an
Order, and issue **Web2 account-bound Tickets**. It is the heaviest single
integration (Stripe Connect + the 収納代行 legal scheme), so it stands alone.

Full money design + legal scheme + counsel flags:
[`payments-design.md`](../../../docs/payments-design.md) (issue #778). Roadmap:
[`ticketing-platform-roadmap.md`](../../../docs/ticketing-platform-roadmap.md).

## What Changes

- **`Order`** — a provider- and method-agnostic purchase record (opaque payment
  references `pi_`/`pm_`, own `status`, `amount`+`currency`, `paid_at`, display
  facets). One Order = **N tickets** (the companion group, ≤
  `max_tickets_per_application`).
- **Off-session winner charge.** Consume a ④ **win** → charge the **saved
  payment method** (from ④'s SetupIntent) via a Stripe **`PaymentIntent`**
  (**destination charge + `on_behalf_of=<organizer>` + `application_fee_amount`**),
  MIT/off-session (no CVC → stays a MIT). **Card-only MVP** (incl. debit/prepaid
  + Apple/Google Pay wallets); konbini/PayPay deferred (async settlement).
- **Web2 account-bound Ticket issuance.** On a **webhook-confirmed** capture,
  issue **N account-bound Tickets** with the applicant's **本人確認** bound so
  each is a **covered ticket (特定興行入場券)**. Never issue on the client confirm.
- **Charge-failure / deadline handoff back to ④.** On failure or a lapsed
  deadline, **no ticket is issued** and ⑤ signals ④ to run **繰上げ**.
- **Payout: hold to event + dispute buffer.** Organizer accounts on **manual
  payout**; release after the event AND a dispute-safety window. This is the
  **primary** buyer→Organizer leg (distinct from ⑦ resale's post-sale seller
  refund).
- **Refund taxonomy.** **Cancellation (中止)** → refund (face + system/発券 fee;
  keep the payment-processor fee, JP norm) via `Refund` + `transfer_reversal`.
  **Postponement (延期)** → no auto-refund; the ticket stays valid for the new
  date. This is the "normal cancellation-refund path" ⑦ official-resale defers to.
- **`ticket-journey` sync.** On issuance, set the user's ticket-journey for the
  event to **PAID** (first-party supersedes the scraped/self-report status).
- **收納代行 scheme.** Organizer = **seller-of-record**; the buyer's obligation is
  **discharged on paying the platform** (代理受領権限); platform is a collection
  agent, **not** MoR / 資金移動業 / 前払式.
- **Webhooks are the source of truth**; **idempotent** handlers; **no PAN/CVC**
  ever touches our systems (Stripe Elements, PCI **SAQ A**).
- **Fee: a single clean %**, buyer-shiftable (organizer cost can be ¥0).

Scope guardrails (MVP): card-only; provider = Stripe Connect (KOMOJU a PoC
challenger, swappable behind the opaque `provider`); no seat maps.

## Capabilities

### New Capabilities
- `ticket-purchase-and-issuance`: the post-win money + issuance pipeline —
  `Order`, off-session winner charge via Stripe Connect (destination charge +
  `on_behalf_of` + `application_fee`), webhook-confirmed **account-bound Ticket
  issuance** (N per order, 本人確認-bound covered tickets), charge-failure
  handoff to ④'s 繰上げ, hold-to-event payout, and the cancellation/postponement
  refund taxonomy under the 収納代行 scheme.

### Modified Capabilities
- `ticket-journey`: issuance adds a **first-party authoritative side-effect
  trigger** that sets a user's journey to `PAID` — a new trigger beyond the
  existing manual / ticket-email-import ones. Specced as a MODIFIED delta
  (`specs/ticket-journey/spec.md`). The Ticket entity itself is **DEFINED here**
  (⑥ ticket-wallet-and-checkin then adds wallet/QR/check-in behavior on it).

## Impact

- **Depends on:** ④ `lottery-application` (the win + saved payment method + 本人確認
  + payment deadline). Hard dependency — ⑤ is un-testable end-to-end without ④.
- **Hands off to:** ⑥ `ticket-wallet-and-checkin` (wallet, rotating QR, same-time
  entry, check-in) operates on the **Ticket** entity defined here.
- **New entities:** `Order`, `Ticket` (account-bound, 本人確認-bound), Payment
  references (opaque). Defined provider-agnostic so a KOMOJU switch is a
  no-proto-break.
- **External:** Stripe Connect (destination charges, Connect accounts, webhooks,
  manual payout, Refund/`transfer_reversal`). **Long-lead prerequisites** (start
  now): Stripe KYC/審査, 収納代行 counsel opinion, 適格請求書発行事業者 registration,
  KOMOJU-vs-Stripe PoC (#778).
- **Legal/compliance (payments-design obligations table):** 総額表示, 特商法
  最終確認画面 + 返品特約, 割賦販売法/PCI SAQ A, 個人情報 越境移転 (Stripe US),
  犯収法 determination, 電子帳簿保存法, 領収書/適格請求書.
