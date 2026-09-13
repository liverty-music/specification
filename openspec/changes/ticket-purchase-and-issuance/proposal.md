## Why

Phase 3 step ⑤. ④ `lottery-application` **authorizes (holds) the card at
application and captures each winner's authorization at the draw** (Stripe
manual-capture; releases losers). This change is the **Order + issuance pipeline**:
take ④'s **captured winning payment**, record an Order, and issue **Web2
account-bound Tickets**. The **money-out layer** (Organizer payout, refund
execution) is a separate capability, **`ticket-settlement-and-payout`**; ⑤ owns the
Order/Ticket + the refund *policy*, settlement owns the money movement.

Full money design + legal scheme + counsel flags:
[`payments-design.md`](../../../docs/payments-design.md) (issue #778). Roadmap:
[`ticketing-platform-roadmap.md`](../../../docs/ticketing-platform-roadmap.md).

## What Changes

- **`Order`** — a provider- and method-agnostic purchase record (opaque payment
  references `pi_`/`pm_`, own `status`, `amount`+`currency`, `paid_at`, display
  facets). One Order = **N tickets** (the companion group, ≤
  `max_tickets_per_application`).
- **Charge is ④'s capture, not a ⑤ off-session charge.** ④ authorizes at apply and
  **captures the winner's held authorization at the draw** (Stripe manual-capture,
  **JPY card only**). ⑤ consumes the **captured winning payment**. **No ⑤-side
  SetupIntent / off-session charge / payment deadline / 繰上げ** — the hold-and-
  capture model removes them.
- **Captured funds already sit on the platform balance.** ④'s charge is a **plain
  platform-account** manual-capture PaymentIntent (no destination charge / no
  `on_behalf_of`), so funds are already held by the platform. The post-event
  `Transfer` of the Organizer's net share (separate charges & transfers) is owned by
  **`ticket-settlement-and-payout`**, not ⑤. *(No ④ migration is needed — the earlier
  "④ shipped a destination charge" premise was wrong.)*
- **`Order`** — a provider/method-agnostic record (opaque `pi_`/`pm_`, own
  `status`, `amount`+`currency`, `paid_at`, facets), one Order = **N tickets**,
  referencing ④'s captured payment.
- **Web2 account-bound Ticket issuance.** On the **webhook-confirmed capture**,
  issue **N account-bound Tickets** with the applicant's **本人確認** bound so each
  is a **covered ticket (特定興行入場券)**. Never issue on the client confirm.
- **Failed capture → no Order/ticket** (the seat is ④'s manual-follow-up concern;
  no ⑤-side retry/繰上げ).
- **Payout: owned by `ticket-settlement-and-payout`.** The hold-to-event Transfer of
  the Organizer's net share (single-Organizer payee + platform fee) lives in the
  settlement capability; ⑤ only records the Order it settles against.
- **Refund taxonomy (⑤ owns the policy; settlement executes).** **Cancellation (中止)**
  → refund (face + system/発券 fee; keep the payment-processor fee, JP norm);
  **postponement (延期)** → no auto-refund, ticket stays valid + a holder-initiated
  window. The `Refund` + `transfer_reversal` **execution** is `ticket-settlement-and-
  payout`. This is the "normal cancellation-refund path" ⑦ official-resale defers to.
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
- `ticket-purchase-and-issuance`: the post-capture Order + issuance pipeline —
  `Order` referencing ④'s **captured** winning payment (a plain platform-account
  charge by ④; funds already platform-held), webhook-confirmed **account-bound Ticket
  issuance** (N per order, 本人確認-bound covered tickets), and the cancellation/
  postponement refund **policy** under the 収納代行 scheme. The payout Transfer + refund
  execution are owned by **`ticket-settlement-and-payout`**. (No ⑤-side off-session
  charge / 繰上げ — ④'s hold model.)

### Modified Capabilities
- `ticket-journey`: issuance adds a **first-party authoritative side-effect
  trigger** that sets a user's journey to `PAID` — a new trigger beyond the
  existing manual / ticket-email-import ones. Specced as a MODIFIED delta
  (`specs/ticket-journey/spec.md`). The Ticket entity itself is **DEFINED here**
  (⑥ ticket-wallet-and-checkin then adds wallet/QR/check-in behavior on it).

## Impact

- **Depends on:** ④ `lottery-application` (the **captured winning payment** from ④'s
  authorize-at-apply/capture-at-draw + 本人確認 + covered-ticket face). Hard
  dependency — ⑤ is un-testable end-to-end without ④.
- **Hands off to:** ⑥ `ticket-wallet-and-checkin` (wallet + in-app dynamic QR +
  check-in) operates on the **Ticket** entity defined here.
- **New entities:** `Order`, `Ticket` (account-bound, 本人確認-bound), Payment
  references (opaque). Defined provider-agnostic so a KOMOJU switch is a
  no-proto-break.
- **Hands off to:** `ticket-settlement-and-payout` (Organizer Connect onboarding,
  post-event `Transfer`, refund/`transfer_reversal` execution) for all money-out.
- **External:** Stripe (Elements for the hold; the Order references ④'s captured
  `pi_`). Settlement's Stripe Connect surface lives in that capability. **Long-lead
  prerequisites** (start now): Stripe KYC/審査, 収納代行 counsel opinion,
  適格請求書発行事業者 registration, KOMOJU-vs-Stripe PoC (#778).
- **Legal/compliance (payments-design obligations table):** 総額表示, 特商法
  最終確認画面 + 返品特約, 割賦販売法/PCI SAQ A, 個人情報 越境移転 (Stripe US),
  犯収法 determination, 電子帳簿保存法, 領収書/適格請求書.
