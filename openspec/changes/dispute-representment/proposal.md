> **Status: proposal only.** Design, specs and tasks are deferred until check-in
> (`ticket-wallet-and-checkin`) ships and records admissions. Tracked under the
> payments research track liverty-music/specification#778 ("Dispute/chargeback
> ops: evidence/representment" in `docs/payments-design.md`).

## Why

A dispute (chargeback) is conceded the moment it opens: on the payment provider's
"dispute created" notice the platform refunds the Order through
RefundOrderUseCase.RefundOrder with the reason Dispute — voiding the Tickets,
reversing the Organizer's payout and marking the Order Refunded — and never
contests it. A dispute can arrive long after the event (card networks allow
months), i.e. after the Settlement was Released, so the platform loses the
charge, the dispute fee and its 5% platform fee even when the holder attended.

Tickets are bound to the buyer's account (and, for verified phases, to a
本人確認 identity), and once `ticket-wallet-and-checkin` records admissions the
platform can prove the holder entered the venue. That evidence is strong against
"product not received" and "unauthorised / not recognised" disputes, so the
platform should contest those instead of conceding.

## What Changes

- **Hold instead of concede.** A newly opened dispute puts the Order into a
  disputed state instead of refunding it; Tickets are not voided and no payout is
  reversed yet. (Whether a disputed ticket may still be used for entry is a
  design question — e.g. block entry while disputed when the event has not
  happened yet.)
- **Submit evidence automatically.** For an Order whose Tickets were admitted,
  the platform submits evidence to the payment provider: the admission records
  (instant, operator, event), the account and 本人確認 binding of the holder, and
  the logged purchase consent / charge-timing disclosure.
- **Settle on the outcome.** On the provider's "dispute closed" notice:
  - **lost** — do what is done today: void the Tickets, reverse the Organizer's
    paid splits, mark the Order Refunded (the platform bears its fee, see
    `components/usecase/order/refund-order`);
  - **won** — the funds return to the platform; the Order returns to Paid and
    nothing is reversed.
- **Concede when there is no case.** A dispute on an Order with no admission
  (event not held yet, or ticket never used) keeps today's behaviour: refund
  immediately.
- **Operator visibility.** Admins can see open disputes and their outcome; the
  Organizer's payout statement shows reversals caused by lost disputes.

## Capabilities

To be confirmed in the specs phase; the likely scope is:

### New Capabilities

- `components/usecase/order/respond-to-dispute`: decide per Order whether to contest or concede a newly opened dispute and submit the evidence.
- `components/usecase/order/settle-dispute`: apply a closed dispute's outcome (won → back to Paid; lost → refund as today).
- `components/entity/order/submit-dispute-evidence`: hand the evidence for a dispute to the payment provider.

### Modified Capabilities

- `components/entity/order` (Purpose): a Disputed status between Paid and Refunded in the state diagram.
- `components/adapter/fan/api/webhook/payment-events`: "dispute created" starts a response instead of a refund; "dispute closed" settles it (today it is acknowledged without effect).
- `components/usecase/order/refund-order`: the Dispute reason is applied only for a lost or conceded dispute.
- `components/entity/ticket` / `components/usecase/ticket/admit` (from `ticket-wallet-and-checkin`): read the admission record as evidence; possibly reject entry while a dispute is open.

## Impact

- **backend**: `stripe_webhook_uc.go` (dispute created/closed handling), `refund_uc.go`, a Stripe dispute-evidence port, Order status migration (new Disputed value).
- **specification**: proto `Order` status enum gains a disputed value (BSR release).
- **frontend / admin console**: dispute visibility for admins; ticket wallet shows a disputed ticket state if entry is blocked.
- **Depends on**: `ticket-wallet-and-checkin` recording admissions (requirement "Admission is recorded as attendance evidence").
- **Ops**: evidence submission has provider deadlines; failures must alert.
