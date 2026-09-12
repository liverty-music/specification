## Why

④ `lottery-application` shipped its Stripe manual-capture flow as a **destination
charge + `on_behalf_of=<organizer>`**, which settles the captured funds to the
Organizer's Stripe balance **immediately at capture** (manual payout only delays
the Organizer's *bank* withdrawal). That means the "hold-to-event escrow" the whole
ticketing scheme (④ payout + ⑤ `ticket-purchase-and-issuance` + ⑦ `official-resale`)
depends on is **not actually in effect** — the platform never custodies the money.
This follow-up moves the charge to **separate charges & transfers** so buyer funds
are genuinely **held on the platform balance** until the event, matching every JP
incumbent (Peatix/ぴあ/TIGET/ZAIKO/LivePocket), Eventbrite, and Stripe's documented
hold-until-event pattern. It must land **before the first live paid sale** (Stripe
KYC 0.1 is still open, so no real charge has run yet — the switch is still free).

Escrow rationale, competitor + Stripe grounding, and the three-axis untangling
(seller-of-record / 収納代行 role / Stripe MoR) live in
[`payments-design.md`](../../../docs/payments-design.md) ("Why separate charges &
transfers"), reconciled with ⑤ in specification PR #936.

## What Changes

- **Capture creates a platform-held charge, not an Organizer-settled one.** At the
  draw, a winning application's held authorization is captured as a **separate
  charge on the platform** (no `transfer_data[destination]` / `on_behalf_of` at
  capture); the platform takes its fee as the **retained** portion. Funds sit on
  the **platform** balance under the 収納代行 scheme. **BREAKING** relative to the
  shipped destination-charge behavior (charge topology + settlement merchant change).
- **Organizer settlement = a post-event `Transfer`.** The Organizer's net share is
  moved by a scheduled platform process only **after the event + dispute buffer**
  (`source_transaction` linking the transfer to the capture) — the payout leg ⑤
  already specifies. Losers' authorizations are still released (cancelled) at the
  draw; refunds/releases come from the platform balance.
- **Statement descriptor** is the platform's by default (platform is now the Stripe
  settlement merchant); attach a **per-event dynamic suffix** to keep dispute rates
  low. Roles stay separate: Organizer = legal seller-of-record (特商法 表記), platform
  = 収納代行 agent + Stripe MoR.
- **`allocated_funds` (funds segregation)** adopted to isolate held funds **when it
  is GA + JP-eligible** (currently a private preview; see the Stripe-confirmation
  task). Ship plain separate charges & transfers first.
- **No behavior change** to: the authorize-at-apply hold, JPY-card/Amex-excluded
  rule, one-application-per-account, the draw algorithm, loser release, 本人確認
  binding, or the ④→⑤ handoff contract (win captured → ⑤ Order + Ticket).

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `lottery-application`: the **"Capture winners and release losers at the draw"**
  requirement changes the captured charge's **custody/topology** — the capture is a
  **platform-held separate charge** (funds on the platform balance) rather than a
  destination charge that settles to the Organizer at capture, with Organizer
  settlement deferred to a post-event `Transfer`. Delta:
  `specs/lottery-application/spec.md`. (⑤ `ticket-purchase-and-issuance` already
  assumes platform-held funds + post-event Transfer via PR #936; no change to ⑤ is
  needed here.)

## Impact

- **Backend (`lottery-application`, shipped):** change the capture path from a
  destination charge to a separate charge (drop `transfer_data`/`on_behalf_of` at
  capture); add/align the post-event `Transfer` (coordinate with ⑤'s payout
  controller so the Transfer is not double-owned). Refund/`transfer_reversal` and
  reserve logic move to the platform balance. First **verify ④'s actual shipped
  charge topology** (task 0) — it may still be stubbed pending Stripe KYC.
- **Stripe Connect config:** platform becomes the settlement merchant; set the
  platform statement-descriptor prefix + per-event suffix; platform must accept
  connected-account **negative-balance responsibility** (also a prerequisite for
  funds segregation).
- **No proto/BSR change** expected — the `Order`/`Payment` model is already
  provider-agnostic (opaque `pi_`/`pm_`); the charge topology is a backend/Stripe
  concern, not a schema one. (Confirm during design.)
- **Gates launch, not other specs.** Must precede the first live paid sale; pairs
  with the 収納代行 counsel opinion (payments-design flag 1) and Stripe KYC (0.1).
