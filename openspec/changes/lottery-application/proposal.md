## Why

Phase 3 step ④ — the first ticketing capability. Organizers can author and
publish events (②), but there is no way to actually **sell** tickets. The MVP
sales method is **lottery only** (roadmap Guiding Decisions): applications open,
close, then a draw runs against a fixed capacity — which removes the hardest
correctness problem (real-time oversell) from the MVP and matches the JP norm
for high-demand concerts.

This change owns the **application + draw** half of the sale. It stops at "won =
the right to be charged": the actual charge, Order, and Ticket issuance are ⑤
`ticket-purchase-and-issuance`. Money design + legal scheme:
[`payments-design.md`](../../../docs/payments-design.md) (issue #778); roadmap:
[`ticketing-platform-roadmap.md`](../../../docs/ticketing-platform-roadmap.md).

## What Changes

- Introduce a first-party **`LotterySalesPhase`** on an organizer-authored Event:
  an application window (open/close), a **capacity accounted in tickets** (sized
  to venue capacity), and a **`max_tickets_per_application`**. Draw runs **after
  applications close** against the fixed capacity.
- **`TicketApplication`** — a fan applies for **1..N tickets** (N ≤
  `max_tickets_per_application`, the companion group), captures **本人確認**
  (applicant name + contact bound to the account), and **saves a payment method
  at application time via a Stripe `SetupIntent`** (`usage=off_session`, 3DS
  once, **no authorization hold**). Decision A: card saved at apply so winners
  are **auto-charged at the draw** (the charge itself is ⑤).
- **1 account / 1 application per phase** (anti-scalp), enforced at application.
- **Automatic draw** at phase close: fair random selection **by application**
  (all-or-nothing per application, so companion groups stay intact) until the
  ticket capacity is filled. Produces **winners** + a **persisted ordered loser
  waitlist** (the draw order).
- **Win / loss outcomes** + a **payment deadline** for winners. On a
  winner-charge failure or deadline lapse (signalled by ⑤), the win is **voided
  and the next waitlisted application is promoted (繰上げ)** — the JP
  "unpaid-by-deadline → void → 繰上げ" convention.
- The persisted **loser draw order** is the demand pool that ⑦ `official-resale`
  and any 二次抽選 consume (satisfies official-resale's ④ dependency).

Scope guardrails (MVP, from roadmap Guiding Decisions): **lottery only** — no
FCFS, **no seat maps, no preference ordering**, single common capacity pool;
capacity in **tickets, not applications**; companion = **same-time entry** (all
won tickets on the lead's device, no distribution). Card-only via ⑤'s provider.

## Capabilities

### New Capabilities
- `lottery-application`: first-party lottery sale of an organizer event —
  `LotterySalesPhase` (window + ticket capacity + `max_tickets_per_application`),
  `TicketApplication` (1..N tickets, 本人確認, saved payment method via
  SetupIntent), 1-account/1-application, automatic by-application draw against
  fixed capacity, win/loss + payment deadline, and the persisted ordered loser
  waitlist for 繰上げ / resale demand.

### Modified Capabilities
<!-- None. LotterySalesPhase is a NEW first-party concept distinct from the
     scraped `sales-phase` (inferred external sales windows); per the roadmap's
     "first-party supersedes scraped" decision the two do not merge and the
     scraped sales-phase spec is unchanged. TicketApplication references the ②
     Event and the ⑤ Order/Payment/Ticket entities but does not modify their
     specs (⑤ is not yet specced; see design.md dependency). -->

## Impact

- **Depends on:** ② `organizer-event-authoring` (shipped) — the Event/Venue an
  application targets and its capacity.
- **Hands off to (not yet specced):** ⑤ `ticket-purchase-and-issuance` consumes
  a **win** → charges the saved card off-session → creates the Order → issues
  Tickets, and signals charge-failure back for 繰上げ. ④ owns the **saved
  payment-method token** (from the SetupIntent) on `TicketApplication`; ⑤ owns
  the charge, Order, Ticket, and refunds.
- **New entities:** `LotterySalesPhase`, `TicketApplication` (with 本人確認 +
  `payment_method` ref + application state), and the persisted loser ordering.
- **New RPCs:** buyer-facing apply / view-my-application / view-result;
  organizer/admin configure-lottery-phase; the draw job.
- **Payments (⑤/#778):** ④ integrates **only the SetupIntent** (card capture +
  save at apply, 3DS once); reuses Stripe Connect. Long-lead items (Stripe KYC,
  収納代行 counsel) should be in flight in parallel.
- **Legal:** 本人確認 capture makes the eventual ticket a **covered ticket
  (特定興行入場券)**; 特商法 最終確認画面 must state the **charge-on-win timing**
  (charged only if you win, at the draw, via the saved card) — see
  payments-design obligations table.
