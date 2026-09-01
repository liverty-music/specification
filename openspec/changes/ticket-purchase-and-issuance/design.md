## Context

See [proposal.md](./proposal.md) for motivation. ⑤ is the money + issuance
pipeline between ④ `lottery-application` (win + saved card + 本人確認 + deadline)
and ⑥ `ticket-wallet-and-checkin` (wallet/QR/check-in on the issued Ticket). The
full money design, 収納代行 legal scheme, counsel flags, and regulatory
obligations table live in [`payments-design.md`](../../../docs/payments-design.md)
(#778) — this design records only the ⑤-specific technical shape, not the
research. ④ is proposed-not-built and ⑥ is not yet specced, so both handoffs are
forward contracts.

## Goals / Non-Goals

**Goals:**
- A correct post-capture pipeline: ④'s captured winning payment → webhook-confirmed
  Order + issuance → account-bound covered tickets, idempotent end-to-end.
- A **provider-agnostic** `Order`/`Ticket`/payment model so a KOMOJU switch or an
  added method is a no-proto-break.
- Stay clearly in the exempt **収納代行** zone (Organizer = business seller-of-
  record; buyer debt discharged on payment; hold-to-event escrow).

**Non-Goals (design-level):**
- The application/draw AND the **card authorization + capture** (④ — Stripe
  manual-capture: authorize at apply, capture winners / release losers at draw);
  the wallet/QR/check-in (⑥). ⑤ has **no off-session charge / SetupIntent / payment
  deadline / 繰上げ**.
- Non-card methods (konbini/PayPay), seat maps, dynamic pricing.
- ⑦ resale's seller-refund leg (different timing/theory; see resale-design.md).

## Decisions

- **Charge = ④'s capture of the held authorization** (Stripe manual-capture,
  destination charge + `on_behalf_of=<organizer>` + `application_fee_amount`, JPY
  card only). The Organizer is the settlement merchant (matches seller-of-record);
  the platform takes the fee. ⑤ does **not** perform a separate charge — it consumes
  ④'s captured payment. (This supersedes the prior SetupIntent/off-session model;
  ④'s auth-hold is enabled by the 30-day JPY authorization window ≫ the ≤14-day
  lottery window — see payments-design.)
- **Issue only on a webhook-confirmed capture, idempotently.** The client
  confirm is never trusted. Idempotency keyed on the provider event id so
  redelivery never double-issues/refunds. Prevents the classic "issued on client
  success, capture later failed" bug.
- **⑤ DEFINES the `Ticket` entity** (account-bound, 本人確認-bound, covered);
  ⑥ adds wallet/rotating-QR/check-in behavior on it. Avoids two capabilities
  each defining a Ticket.
- **`Order`/`Payment` provider-agnostic** (opaque `pi_`/`pm_`, own status, no raw
  provider status, no PAN/CVC). Keeps the proto stable across a provider switch.
- **Entity conventions (proto stage).** `Order`, `Ticket`, and all IDs MUST follow
  the repo convention (CLAUDE.md): **wrapper-message type-safe IDs** (`OrderId`,
  `TicketId`, a `PaymentRef` wrapper) and an **enum** for `Order.status`, with
  protovalidate constraints — the spec's status names (`pending`/`paid`/...) are
  logical values, not proto bare-string literals.
- **Payout hold-to-event + dispute buffer** via manual payout — the escrow-with-
  counter-performance gate that supports the 収納代行 characterization (the gate
  matters, not a bright-line N-day; see payments-design determination).
- **Refund taxonomy: cancellation (中止) refunds; postponement (延期) does not**
  (ticket stays valid for the new date). Keep the processor fee (JP norm). This
  is the "normal cancellation-refund path" ⑦ resale defers to — and note ⑦'s
  seller-refund leg is a **different** structure (post-sale, not hold-to-event).
- **No charge-failure/繰上げ path in ⑤.** ④'s hold-and-capture model has no payment
  deadline or off-session failure → no 繰上げ; a rare failed capture leaves the seat
  unfilled (④'s manual follow-up). The ④→⑤ contract is "win captured → ⑤ Order +
  Ticket | capture failed → no Order".
- **ticket-journey → PAID on issuance** as the first-party authoritative status.
  Expressed as a requirement of this capability (⑤ writes ticket-journey); the
  formal ticket-journey capability delta, if warranted, is folded in at apply.

## Risks / Trade-offs

- **Authored ahead of ④ (not built) and ⑥ (not specced).** *→* Reference, do not
  redefine, ④'s win/saved-pm and keep ⑥'s wallet/QR out of scope; express both
  handoffs as states + signals. Reconcile shapes when ④ builds / ⑥ specs.
- **Auto-charge burst at draw close** (many winners charged at once). *→* Batch
  with per-Order idempotency keys; rate-limit to the provider; retries safe.
- **Chargebacks land after payout window.** *→* Hold a reserve past the dispute
  window; `transfer_reversal` clawback; evidence retained (payments-design).
- **收納代行 boundary is substance-over-form.** *→* Keep the discharge clause +
  counter-performance gate + business-payee; the counsel opinion (#778 flag 1) is
  a launch prerequisite, not a spec blocker.
- **Long-lead externals** (Stripe KYC, counsel, 適格請求書 registration, KOMOJU
  PoC) gate **launch**, not spec authoring. *→* Start now in parallel (tasks §0).
- **Provider lock-in.** *→* The opaque provider-agnostic Order/Payment keeps the
  KOMOJU switch a config/adapter change, not a proto break.

## Migration Plan

New capability; defines Order/Ticket. Sequence when implementing: proto
(Order, Ticket, payment refs, RPCs) → BSR → backend (Connect charge adapter,
webhook ingest + idempotent issuance, payout controller config, refund/
`transfer_reversal`, ④ signal consumer/emitter) → frontend (checkout via Elements
is mostly in ④'s apply; ⑤ surfaces order/ticket state) → console (payout/refund
ops). Gated on ④ for end-to-end; long-lead externals in §0 must clear before a
live sale.

## Open Questions

- **Exact dispute-buffer / payout-release length** — a tunable operational
  parameter (the escrow gate, not the duration, is load-bearing); set with
  payment ops. Does not change the spec surface.
- **Batch/rate-limit strategy for the draw-close charge burst** — an
  implementation detail, not a spec change.
