> **Status: proposal only.** Admissions are recorded since `ticket-wallet-and-checkin`
> (archived 2026-10-10). Design, specs and tasks are written after
> `unify-order-issuance` and `resell-tickets-by-lottery` are archived, so the deltas
> build on their Order, refund and payment-events texts. Tracked under the
> payments research track liverty-music/specification#778 ("Dispute/chargeback
> ops: evidence/representment" in `docs/payments-design.md`).

## Why

A dispute (chargeback) is conceded the moment it opens: on the payment provider's
"dispute created" notice the platform refunds the Order through
OrderUseCase.Refund with the reason Dispute — voiding the Tickets,
reversing the Organizer's payout and marking the Order Refunded — and never
contests it. A dispute can arrive long after the event (card networks allow
months), i.e. after the Settlement was Released; the Organizer's split is clawed
back, so the platform still loses its platform fee (the Organizer's own rate) and the
provider's dispute fee — even when the fan attended.

Tickets are bound to the fan's account (and, for verification-required sales, to a
本人確認 identity), and once `ticket-wallet-and-checkin` records admissions the
platform can prove the fan entered the venue. That evidence is strong against
"product not received" and "unauthorised / not recognised" disputes, so the
platform should contest those instead of conceding.

## What Changes

- **Hold instead of concede — only when there is evidence.** A newly opened
  dispute on an Order with at least one admitted Ticket puts the Order into a
  disputed state instead of refunding it; no payout is reversed yet. Such an
  Order's event has already happened, so its Tickets are not blocked.
- **Submit evidence automatically.** For an Order whose Tickets were admitted,
  the platform submits evidence to the payment provider: the Admissions
  (admit time, scanner, event) and the account and 本人確認 binding of the fan.
  The checkout shows the charge-timing disclosure but records no consent; storing
  it is a prerequisite to add here before it can be evidence.
- **Settle on the outcome.** On the provider's "dispute closed" notice:
  - **lost** — do what is done today: void the Tickets, reverse the Organizer's
    paid splits, mark the Order Refunded (the platform bears its fee, see
    `components/usecase/order/refund`);
  - **won** — the funds return to the platform; the Order returns to Paid and
    nothing is reversed.
- **Concede when there is no case.** A dispute on an Order with no admitted
  Ticket — the event has not happened yet, or the ticket was never used — keeps
  today's behaviour: refund immediately (voiding the Tickets).
- **Admin visibility.** Admins can see open disputes and their outcome; the
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
- `components/usecase/order/refund`: the Dispute reason is applied only for a lost or conceded dispute.
- `components/entity/admission/get-by-ticket`: read the Admissions of a Ticket as evidence.

## Impact

- **backend**: `stripe_webhook_uc.go` (dispute created/closed handling), `refund_uc.go`, a Stripe dispute-evidence port, Order status migration (new Disputed value).
- **specification**: proto `Order` status enum gains a disputed value (BSR release).
- **frontend / admin console**: dispute visibility for admins.
- **Depends on**: Admissions (`components/entity/admission`, "kept as chargeback evidence"), and the Order, refund and payment-events texts as `unify-order-issuance` and `resell-tickets-by-lottery` leave them. Under `publish-events-through-outbox`, a dispute that returns an Order to Paid must not announce it as paid again.
- **Ops**: evidence submission has provider deadlines; failures must alert.
