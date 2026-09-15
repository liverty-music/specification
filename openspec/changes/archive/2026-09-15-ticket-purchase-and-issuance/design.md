## Context

See [proposal.md](./proposal.md) for motivation. ⑤ is the Order + issuance pipeline
between ④ `lottery-application` (**authorize-at-apply → capture-at-draw** + 本人確認,
now SHIPPED) and ⑥ `ticket-wallet-and-checkin` (wallet/QR/check-in on the issued
Ticket). The full money design, 収納代行 legal scheme, counsel flags, and regulatory
obligations table live in [`payments-design.md`](../../../docs/payments-design.md)
(#778) — this design records only the ⑤-specific technical shape, not the research.
**④ is shipped**; the ④→⑤ handoff is ④'s **Won-captured** signal (④ owns the
PaymentIntent + its webhooks; MVP handoff = the Won-captured record, no event).
identity-ekyc adds a `verification_level` ⑤ consumes; ⑥ is not yet built.

## Goals / Non-Goals

**Goals:**
- A correct post-capture pipeline: ④'s **Won-captured** signal → Order + issuance
  → account-bound covered tickets, idempotent end-to-end.
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

- **Charge = ④'s capture of the held authorization** (Stripe manual-capture, JPY
  card only). ⑤ does **not** perform a separate charge — it consumes ④'s captured
  payment. (This supersedes the prior SetupIntent/off-session model; ④'s auth-hold
  is enabled by the 30-day JPY authorization window ≫ the ≤14-day lottery window —
  see payments-design.)
- **Money-out (settlement/payout) is owned by `ticket-settlement-and-payout`, not ⑤.**
  ④'s charge is a **plain platform-account** manual-capture PaymentIntent (verified in
  backend: no `TransferData`/`OnBehalfOf`/`ApplicationFee`), so captured funds **already
  land on the platform balance** — the "charge" half of separate charges & transfers is
  already correct. The missing "transfers" half (Organizer Connect onboarding, post-event
  `Transfer` of the Organizer's net share with the platform fee retained, hold-to-event
  gate, refund/`transfer_reversal`) is the new **`ticket-settlement-and-payout`**
  capability. ⑤ records the Order that settlement settles against; it does **not** perform
  the payout. *(The earlier "④ shipped a destination charge → ⑤/④ follow-up must migrate
  to separate charges & transfers" premise was **factually wrong** and is withdrawn — ④
  never used a destination charge.)*
- **Trigger = ④'s Won-captured signal, NOT a ⑤-owned capture webhook (corrected).**
  ④ owns the Stripe PaymentIntent lifecycle (authorize/capture/cancel) and its
  webhooks; on capture success ④ marks the application **Won-captured**. ⑤ keys
  issuance on that signal (MVP: the Won-captured record; a later event is additive).
  The earlier "issue on a ⑤-owned capture webhook / webhooks are the source of
  truth for capture" wording was a leftover from the off-session-charge model and
  is corrected — ⑤ owns only the **refund/dispute** webhooks (from its own refund
  calls) + **issuance idempotency**.
- **Capture-succeeded / issuance-failed reconciliation.** ④ delegated post-capture
  issuance-failure to ⑤: retry issuance idempotently; if it still can't complete,
  **refund the captured payment** (Refund + `transfer_reversal`) and flag for
  follow-up — never money-captured-with-no-ticket, never double-issue.
- **Covered-ticket 本人確認 source depends on the phase verification requirement.**
  Where the phase required identity verification (identity-ekyc), the **verified
  identity is authoritative** (bound name = verified 本人確認, no conflicting
  self-declared name); otherwise ④'s self-declared name+contact binds. Resolves the
  identity-ekyc "fold-in" for ⑤.
- **No `pending` Order.** ⑤ creates the Order from an already-captured payment, so
  it is `paid` on creation (pre-capture authorize/hold state lives on ④'s
  `TicketApplication`). Order states: `paid` → `refunded` (or `failed` for the
  capture-succeeded-but-issuance-refunded edge).
- **Postponement offers a holder-initiated refund window** (JP norm) in addition to
  "ticket stays valid for the new date"; cancellation refunds the current holder.
  *Window-start (modeled in follow-up 4.2):* the bounded window is measured from the
  **reschedule/announcement date**, now carried by a **server-owned
  `Event.rescheduled_time`** (`RescheduledTime`, OUTPUT_ONLY) — stamped by the platform
  when the organizer reschedules, independent of the refund caller. Measuring the window
  from the purchase/capture time (`Order.paid_at`) would be wrong (it would reject every
  advance-purchase refund), and a window-start supplied on `RefundOrderRequest` (#938) is
  NOT sufficient — it would be set by the same admin caller the window is meant to
  constrain, giving no independent check. Remaining backend follow-up: stamp
  `rescheduled_time` on the organizer reschedule flow and gate `RefundOrder(POSTPONEMENT_WINDOW)`
  against `now ≤ rescheduled_time + window`. Until that lands the admin call stays
  authoritative (the platform enforces the window operationally).
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
- **Payout hold-to-event + dispute buffer — relocated to `ticket-settlement-and-payout`.**
  The hold-to-event gate, the post-event `Transfer`, and the single-Organizer-payee +
  platform-fee split all live in the settlement capability. ⑤ only needs the Order to
  reference ④'s captured charge so settlement can `Transfer` against it
  (`source_transaction`).
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

- **④ is shipped; ⑥ not yet built.** *→* Bind ⑤ to ④'s actual **Won-captured**
  handoff (not a saved-card/off-session charge); keep ⑥'s wallet/QR out of scope
  and reconcile the Ticket shape when ⑥ builds.
- **Auto-charge burst at draw close** (many winners charged at once). *→* Batch
  with per-Order idempotency keys; rate-limit to the provider; retries safe.
- **Chargebacks land after payout window.** *→* Hold a reserve past the dispute
  window; `transfer_reversal` clawback; evidence retained (payments-design).
- **收納代行 boundary is substance-over-form.** *→* Keep the discharge clause +
  counter-performance gate + business-payee; the counsel opinion (#778 flag 1) is
  a launch prerequisite, not a spec blocker.
- **Long-lead externals** (Stripe KYC, counsel, 適格請求書 registration) gate
  **launch**, not spec authoring. *→* Start now in parallel (tasks §0). (Provider
  is decided: Stripe Connect — no KOMOJU PoC; the opaque `provider` keeps a future
  swap an adapter change.)
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
