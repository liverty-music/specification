## Why

Phase 3 step ④ — the first ticketing capability. Organizers can author and
publish events (②), but there is no way to actually **sell** tickets. The MVP
sales method is **lottery only** (roadmap Guiding Decisions): applications open,
close, then a draw runs against a fixed capacity — which removes the hardest
correctness problem (real-time oversell) from the MVP and matches the JP norm
for high-demand concerts.

This change owns the **application → draw → payment** pipeline of a lottery
sale: a fan's card is **authorized (held) at application**, the winners' holds
are **captured at the draw**, and the losers' holds are **released**. It stops at
the captured payment: turning a captured winner into an **Order + issued Ticket**
is ⑤ `ticket-purchase-and-issuance`. Money design + legal scheme:
[`payments-design.md`](../../../docs/payments-design.md) (issue #778); roadmap:
[`ticketing-platform-roadmap.md`](../../../docs/ticketing-platform-roadmap.md).

## What Changes

- Introduce a first-party **`LotterySalesPhase`** on an organizer-authored Event:
  an **application window of 1–14 days (default 10)**, a **capacity accounted in
  tickets** (sized to venue capacity by the organizer), and a
  **`max_tickets_per_application`**. Draw runs **after applications close** against
  the fixed capacity.
- **`TicketApplication`** — a fan applies for **1..N tickets** (N ≤
  `max_tickets_per_application`, the companion group), captures **本人確認**
  (applicant name + contact bound to the account), and **authorizes (holds) the
  ticket amount at application via a Stripe manual-capture card payment**
  (`capture_method=manual`, 3DS completed once, **JPY only, American Express not
  accepted**). No money is captured at application — only held.
- **1 account / 1 application per phase** (anti-scalp), enforced at application.
- **Automatic draw** at phase close: fair random selection **by application**
  (all-or-nothing per application, so companion groups stay intact) until the
  ticket capacity is filled. Produces **winners** + a **persisted ordered loser
  waitlist** (the random draw order).
- **At the draw:** each **winner's** authorization is **captured** (the charge);
  each **loser's** (and each withdrawn application's) authorization is
  **released/cancelled**. Captured winners are handed to ⑤ for Order + Ticket
  issuance. **No payment deadline, no post-draw active payment step, no winner
  decline** — the JP incumbent (ぴあ/ローチケ) "held at apply, charged on win,
  released on loss" model.
- **No automatic 繰上げ in the MVP.** With funds held, a winner's capture
  effectively never fails and there is no unpaid-by-deadline / decline trigger, so
  繰上げ's reasons vanish; a rare failed capture leaves the seat unfilled (manual
  follow-up). The persisted **loser draw order** is still stored as the demand
  pool that ⑦ `official-resale` and any future 二次抽選 consume (satisfies
  official-resale's ④ dependency).

Scope guardrails (MVP, from roadmap Guiding Decisions): **lottery only** — no
FCFS, **no seat maps, no preference ordering**, single common capacity pool;
capacity in **tickets, not applications**; companion = **same-time entry** (all
won tickets on the lead's device, no distribution). **Card only** (JPY,
Visa/Mastercard/JCB/Diners/Discover; Amex excluded); **no automatic 繰上げ**.

## Capabilities

### New Capabilities
- `lottery-application`: first-party lottery sale of an organizer event —
  `LotterySalesPhase` (1–14-day window + ticket capacity +
  `max_tickets_per_application`), `TicketApplication` (1..N tickets, 本人確認,
  card **authorization/hold** via manual-capture at apply), 1-account/1-application,
  automatic by-application draw against fixed capacity, **capture winners / release
  losers at the draw**, win/loss results, and the persisted ordered loser waitlist
  for ⑦ resale demand.

### Modified Capabilities
<!-- None. LotterySalesPhase is a NEW first-party concept distinct from the
     scraped `sales-phase` (inferred external sales windows); per the roadmap's
     "first-party supersedes scraped" decision the two do not merge and the
     scraped sales-phase spec is unchanged. TicketApplication references the ②
     Event and the ⑤ Order/Ticket entities but does not modify their specs (⑤ is
     not yet specced; see design.md dependency). -->

## Impact

- **Depends on:** ② `organizer-event-authoring` (shipped) — the Event/Venue an
  application targets.
- **Hands off to (not yet specced):** ⑤ `ticket-purchase-and-issuance` takes a
  **captured winning payment** → creates the Order → issues Tickets (N per order),
  and owns refunds (incl. event-cancellation and any post-capture issuance
  failure). ④ owns the **authorization + capture/cancel** on `TicketApplication`;
  ⑤ owns the Order, Ticket, and refunds.
- **New entities:** `LotterySalesPhase`, `TicketApplication` (with 本人確認 +
  payment-authorization ref + application state), and the persisted loser ordering.
- **New RPCs:** buyer-facing apply / withdraw / view-my-application / view-result;
  organizer configure-lottery-phase + view-status; the draw job (capture winners /
  cancel losers).
- **Payments (⑤/#778):** ④ integrates Stripe **manual-capture** (authorize at
  apply, capture on win / cancel on loss at the draw); reuses Stripe Connect.
  **JPY only, Amex excluded** — required so the authorization can be held for the
  window (a JP-based Stripe account holds JPY card authorizations up to 30 days;
  the 1–14-day window stays well within it). Long-lead items (Stripe KYC, 収納代行
  counsel — incl. hold-vs-capture treatment) should be in flight in parallel.
- **Legal:** 本人確認 capture makes the eventual ticket a **covered ticket
  (特定興行入場券)**; 特商法 最終確認画面 must state the **charge-on-win timing**
  (the card is **authorized at application, charged only if you win at the draw,
  and released if you lose**) and 総額表示 — see payments-design obligations table.
