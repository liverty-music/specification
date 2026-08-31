## Context

See [proposal.md](./proposal.md) for motivation. The full legal + competitor
research and every settled decision (D1–D7) live in
[`docs/resale-design.md`](../../../docs/resale-design.md) — this design records
only the technical shape and the *why* behind the decisions; it does not restate
the research.

This capability is **authored ahead of its dependencies**. It reuses primitives
that are designed but **not yet specced or built**: ④ `lottery-application` (the
loser demand pool), ⑤ `ticket-purchase-and-issuance` (Order/Payment/Ticket +
Stripe Connect 収納代行 + refunds — see [`payments-design.md`](../../../docs/payments-design.md),
issue #778), and ⑥ `ticket-wallet-and-checkin` (issue / void / rotating-QR /
本人確認 binding). The design must stay coherent with those; implementation is
gated on them shipping.

## Goals / Non-Goals

**Goals:**
- A sanctioned face-value resale path that is legally safe by construction (buyer
  leg = 収納代行 to a business Organizer; seller leg = refund of own payment fitting
  the 資金決済法 2条の2第2号 escrow exclusion → no 資金移動業; no inventory → no
  古物商許可; blanket consent → compliant 不正転売禁止法) and reuses ⑤'s payment
  scheme unchanged.
- A single new domain entity (`ResaleListing`) that references existing money
  primitives rather than introducing a new one.

**Non-Goals (design-level):**
- Above-face or dynamic pricing; buyer-side markup; P2P transfer; physical-ticket
  handling — all excluded to preserve the legal posture.
- Payment provider mechanics — owned by ⑤/payments-design.md, reused as-is.
- Organizer-buyback of unsold listings (D6 — return-only in MVP; チケプラTrade offers
  buyback, deferred).
- Match-turn push/email notification (deferred to a future change; MVP surfaces the
  offer in-app).
- Seat maps / preference ordering in the demand queue (defer; MVP is a flat
  priority-ordered queue).

## Decisions

- **D1 — Seller refund triggered on resale completion, held-back ~days to ~3 weeks
  (a fixed window measured from the match), NOT tied to the event.** Confirmed against every JP incumbent (ticket board 定価トレード
  day-after + ~2-3wk transfer, e+ ~1-2wk, ぴあ ~3wk, tiget on 成立 via card reversal);
  **none hold to the event**. Legal fit: 2条の2第2号 counter-performance = the
  seller's ticket delivery (void+reissue at match), not the event — so settling
  after the match satisfies the escrow exclusion; holding to the event is
  unnecessary and (per counsel) weakens rather than strengthens it. Chargeback is
  managed by a short hold-back reserve + delivered-ticket/entry evidence +
  `transfer_reversal`, as incumbents run it. *Reverses the earlier "after-event"
  lean* — that was rejected as non-standard and legally weaker, not stronger.
- **D2 — Mandatory-by-default enablement, no organizer off-switch.** The law
  requires *organizer consent*, not per-event revocability; a blanket standing
  grant in the vetted-Organizer platform agreement satisfies it for all their
  events. Alternative (per-event opt-in) leaves "resale deserts" where scalpers
  thrive and adds a toggle UI. Mandatory-by-default maximizes consumer protection
  + anti-scalp coverage and is *simpler* for MVP. Genuine incompatibilities are
  handled by **automatic structural exclusions** (a derived property of the
  ticket type), not organizer preference; rare contractual carve-outs go through
  an **admin exception**, not a self-serve switch.
- **D3 — Deadline `start_time − 1h`.** Uses the Event's `start_time` (not
  `open_time`) so buyers still have time to reach the venue; organizer may set an
  earlier cutoff, never later.
- **D4 — Seller bears a single clean fee (~10% default, within an 8–12% band);
  buyer pays face.** The fee targets covering the ~7.2% round-trip card processing
  (refund leg + fresh-sale leg) plus margin, matching ぴあ/ローチケ (~10%). The exact
  point in the band is set together with the **税抜/税込 decision**: if 税込, the
  effective take is ~9.1% after consumption tax, so the setting may sit toward the
  top of the band to preserve margin — i.e. ~10% is the default anchor, not a
  final number until 税抜/税込 is chosen. Alternative (tiget's ¥220 flat) only works
  on low-price indie tickets and would not cover processing at ¥5,000–10,000 face.
  Buyer-side markup is rejected (consumer-hostile, and face-value-only is a legal
  must).
- **D5 — Public marketplace with lottery-loser priority, not first-come.**
  Inventory is publicly visible/joinable (discoverability + liquidity like
  ぴあ/ローチケ), but matching is priority-ordered: losers-first (draw order), then
  general public (join order); a seat is offered **sequentially** with a
  per-candidate timed window, and re-queues (not dead) if it exhausts the queue
  before the deadline. First-come was rejected (thundering herd + unfair to
  earliest applicants); waitlist-only was refined to a public marketplace to
  recover the discoverability incumbents expose.
- **D6 — Unsold = return-only, no organizer buyback in MVP.** Return the ticket to
  the holder; a buyback safety net (チケプラTrade) is deferred.
- **D7 — Mandatory-by-default resale holds even against an artist no-resale rider;
  the admin exception is the mechanism** (an Organizer bound upstream cannot grant
  consent, so the rare admin-approved exclusion covers it — sufficient for MVP).
- **Entity: `ResaleListing`.** Holds `ticket_id`, `seller`, `state`
  (LISTED/OFFERED/SOLD/WITHDRAWN/EXPIRED), `listed_at`, derived face price (券面代金),
  resale fee, `matched_buyer`, `sold_at`, `refund_settled_at`. Money references
  point at the seller's original `Payment` (refund leg) and the buyer's new `Order`
  (sale leg); no new money primitive.
- **`OFFERED` in-flight state.** Between LISTED and SOLD a seat is locked to one
  candidate for a timed window; withdrawal is allowed only in LISTED, resolving the
  withdraw-vs-purchase race.
- **Atomic match transaction.** Settle buyer payment → void original ticket
  (invalidate rotating QR) → issue new ticket + re-bind 本人確認, all-or-nothing.
  The seller refund is **triggered by the same completion** (with a hold-back
  reserve before release), NOT gated on the event.
- **Netting.** The buyer's fresh payment replenishes the balance the seller's own
  refund is drawn from, so the Organizer settles the seat once (never double-paid).

## Risks / Trade-offs

- **Authored ahead of ④⑤⑥** → the entity/RPC shapes here may need reconciliation
  when those specs land. *Mitigation:* keep `ResaleListing` referencing (not
  redefining) Order/Payment/Ticket; tasks.md is gated on ④⑤⑥ so nothing is built
  until they exist.
- **Chargeback after the seller is settled** (settlement is weeks post-sale, but a
  dispute can arrive later). *→* Hold a reserve for the hold-back period past the
  dispute window and claw back via `transfer_reversal` (⑤'s tooling); the
  delivered-ticket / entry evidence supports representment. This is exactly how
  ぴあ/ticket board run post-sale settlement.
- **返品特約 must be shown, or the 8-day 通信販売 return right applies to the buyer.**
  *→* Required as a distinct spec item (final confirmation screen, 特商法 §12-6);
  fee framed as 役務対価 to lower 消費者契約法 §9/§10 risk. Counsel brief item 6.
- **Blanket consent + artist no-resale rider (D2/D7).** *→* Admin exception covers
  the rider case; counsel brief item 5 confirms blanket consent satisfies
  不正転売禁止法. Do not launch mandatory-by-default until confirmed.
- **Fee margin depends on 税抜/税込 (消費税/インボイス).** *→* If 税込, effective
  margin ~9.1%; decide fee presentation (counsel brief item 8). May force fee toward
  the top of the 8-12% band.
- **PII lifecycle for 本人確認.** *→* Define 利用目的 + retention-through-hold-back +
  deletion (counsel brief item 7).
- **Depends on ⑤/⑥ substrate** — Ticket/Order/Payment entities, resale-eligibility
  metadata (free/comp/bundled/name-locked), the blanket-consent flag, and ④'s
  persisted loser ordering all live in the not-yet-specced ④⑤⑥. *→* Keep
  `ResaleListing` referencing (not redefining) them; tasks §0 gates on ④⑤⑥ so
  nothing is built until they exist and host these fields.

## Migration Plan

Spec-only now; no code ships until ④⑤⑥ are specced and built. Sequence when
unblocked: extend ⑤/⑥ ticket entity with resale-eligibility metadata + the
required-event-info sales gate → add `ResaleListing` + RPCs → wire the seller
refund to the resale-completion trigger with a hold-back reserve → enable per
Organizer via the platform-agreement consent flag. No rollback concern at the spec
stage.

## Open Questions

- Exact **offer-window duration** and **hold-back / dispute-reserve length** —
  tunable operational parameters that do not change the specs or task breakdown;
  set with ⑤'s payment ops when building.
- **Fee 税抜 vs 税込** presentation (affects effective margin) — a business/finance
  decision, resolvable with the fee value; does not change the spec surface.
