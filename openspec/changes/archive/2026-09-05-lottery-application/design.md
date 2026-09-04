## Context

See [proposal.md](./proposal.md) for motivation. ④ is the first ticketing
capability; it owns the **application → draw → payment (authorize + capture)**
pipeline of a lottery sale and hands a **captured winning payment** to ⑤
`ticket-purchase-and-issuance` for the Order/Ticket. Money design + legal scheme:
[`payments-design.md`](../../../docs/payments-design.md) (#778). Depends on ②
`organizer-event-authoring` (shipped) for the **published Event** it attaches a
phase to. **Note (existing-model reality):** neither ② nor the Event/Venue proto
exposes a **capacity** field, so ④ does **not** read a venue capacity — the
**Organizer sets the phase capacity** (sized to the venue by their own knowledge).
Publish/visibility state lives on the **concert/Series**, not the Event, so ④
gates on the concert being `PUBLISHED`. ⑤/⑥ are not yet specced, so the issuance
handoff shape here is a forward contract.

## Goals / Non-Goals

**Goals:**
- A correct, oversell-free lottery: draw against a **fixed capacity after
  applications close** (no real-time inventory race).
- Anti-scalp from day one: **1 account / 1 application** + **本人確認**.
- The simplest correct payment model: **funds held at apply, captured on win,
  released on loss** — no payment deadline, no failure/re-auth machinery.
- A **persisted loser draw order** that ⑦ official-resale (and future 二次抽選)
  reuse.

**Non-Goals (design-level):**
- FCFS/real-time sales, **seat maps, preference ordering**, multiple parallel
  pools — deferred (roadmap Guiding Decisions).
- The **Order**, Ticket issuance, and refunds — all ⑤ (④ stops at the captured
  payment).
- **Automatic 繰上げ** — deferred (see decision below).
- Companion ticket **distribution** — none; same-time entry is ⑥.

## Decisions

- **D-A — Payment = authorization hold (Stripe manual capture); capture on win,
  release on loss (user-confirmed).** At apply, **authorize (hold)** the ticket
  amount via a Stripe card PaymentIntent with `capture_method=manual` (3DS once,
  CIT at apply — no separate SetupIntent). At the draw, **capture** each winner's
  authorization and **cancel** each loser's/withdrawn's. This is the JP incumbent
  (ぴあ/ローチケ) model. **Rejected — SetupIntent + off-session charge at draw
  (prior D-A):** an off-session charge can fail / need 3DS re-auth, which forces a
  payment-deadline clock, grace/re-auth links, and 繰上げ-on-failure — the hold
  model removes all of that. **Rejected — no card at apply, winners actively pay
  post-draw:** drops the frictionless auto-charge and risks winner abandonment.
  **Enabler:** a **JP-based Stripe account holds JPY card authorizations up to 30
  days** (Visa/Mastercard/JCB/Diners/Discover); the 1–14-day window (D-window) stays
  well within it. **Cost:** the fan's funds are held for up to the window length
  (debit/prepaid included) — accepted (ローチケ norm; bounded by the window).
- **D-cards — JPY only, American Express excluded.** The 30-day authorization
  window applies only to JPY transactions on Visa/Mastercard/JCB/Diners/Discover.
  Amex and non-JPY fall back to the standard ~7-day authorization, too short to
  guarantee capture at the draw, so they are **rejected at application**.
- **D-window — application window is 1–14 days, default 10.** The organizer sets
  open/close; the duration MUST be within **[1 day, 14 days]** (enforced in proto
  protovalidate + the usecase). **Default 10 days** is a console pre-fill (proto3
  has no message-field default and the value is derived, so the default lives in
  the organizer console, not the wire). Rationale: 14 days ≪ the 30-day hold
  ceiling (comfortable margin), and it bounds how long a fan's funds are held.
- **Draw unit = the whole application (all-or-nothing).** A winning application
  wins **all** its requested tickets so companion groups stay intact; capacity is
  counted in **tickets**. Rejected: drawing individual tickets (would split
  groups).
- **Draw algorithm = uniform-random order + greedy fit.** Shuffle applications
  uniformly at random; admit each application whose ticket count **fits the
  remaining capacity**, waitlist the rest **in that same random order**; continue
  past a too-large application so smaller later ones can still fill capacity.
  **Fairness note:** because the order is a uniform random shuffle, "admit the
  next application that fits" is equivalent to a uniform random draw among the
  fitting applications — there is no merit ranking to violate, so the skip-large
  behavior is fair (a larger group is simply likelier to not fit; accepted for
  MVP). Capacity is never oversold.
- **Persisted ordered loser waitlist — of losing applications (per account).**
  The random draw order of non-winning **applications** is stored (each is one
  account's companion group). In the MVP ④ does **not** itself consume it (no
  auto-繰上げ); it is the single source for ⑦ official-resale's demand pool (and a
  future 二次抽選). **Projection for ⑦:** a losing application maps to **one demand
  candidate (that account)** in draw order — ⑦'s per-seat offer queue derives
  candidates from this application ordering (not one entry per requested ticket).
  The timestamp-order fallback in ⑦'s older draft is superseded (④ always persists
  the random order — do NOT use timestamp order, it would be FCFS-unfair).
- **No automatic 繰上げ in the MVP.** With funds held and captured at the draw, a
  winner's capture effectively never fails, and there is no unpaid-by-deadline or
  pre-charge-decline trigger — 繰上げ's reasons do not occur. A rare failed capture
  (e.g. the card was closed/frozen between apply and draw) leaves that seat
  **unfilled** (logged for manual follow-up), not auto-promoted. Re-introducing
  automated 繰上げ later would require re-authorizing a released loser's hold
  (reintroducing failure handling); deferred until there's demand for it. The
  loser waitlist is still persisted for ⑦.
- **1 account / 1 application per phase**, **withdrawable before the draw** (which
  **releases the hold**); a fan may re-apply while the window is open. **No winner
  decline** — capture happens at the draw with no gap for the fan to decline; the
  cannot-attend path after issuance is ⑦. An issued ticket is not ④-withdrawable.
- **`LotterySalesPhase` is a NEW first-party concept**, distinct from the scraped
  `sales-phase` (inferred external windows). The roadmap's shorthand "extends
  sales_phase" is **superseded**: per "first-party supersedes scraped" they do
  **not** merge and the scraped spec is unchanged; the name is kept but the entity
  is independent (no delta on scraped `sales-phase`). Roadmap wording updated to
  match.
- **Entity conventions (proto stage).** `LotterySalesPhase`, `TicketApplication`,
  and all IDs MUST follow the repo convention (CLAUDE.md): **wrapper-message
  type-safe IDs** and **enums** for states (not bare strings), protovalidate
  constraints. The spec's status names are logical, not proto string literals.
- **④/⑤ boundary (capture is in ④).** ④ owns: `LotterySalesPhase`,
  `TicketApplication` (incl. the payment-authorization ref + 本人確認), the draw,
  **capturing winners / cancelling losers**, win/loss, and the persisted loser
  waitlist. ⑤ owns: **Order** creation, **Ticket** issuance from a captured
  payment, and **refunds** (event-cancellation and any post-capture issuance
  failure). The contract is "win → ④ captures → hands the captured payment to ⑤ →
  Order + Ticket".

## Risks / Trade-offs

- **Fan funds held up to the window length.** Debit/prepaid balances are reserved
  for up to 14 days. *→* Accepted (ローチケ norm); the 1–14-day window bounds it,
  and losers are released the moment the draw runs.
- **Capture-then-issuance gap.** ④ captures at the draw before ⑤ issues; if ⑤'s
  issuance fails, money is captured without a ticket. *→* ⑤ owns idempotent
  issuance + refund-on-failure; ④ hands off the captured payment and records the
  win, ⑤ reconciles. Keep `TicketApplication` referencing (not defining) the ⑤
  Order/Ticket.
- **Authored partly ahead of ⑤.** The captured-payment → Order/Ticket handoff is
  a forward contract; shapes may need reconciliation when ⑤ is specced. *→*
  Express the handoff as an application state + the captured-payment ref, not ⑤'s
  internals.
- **Amex / non-JPY excluded.** Some fans can't use their preferred card. *→*
  Accepted for MVP; required by the 30-day-hold constraint. Revisit if Amex volume
  matters (would need a shorter window or a different flow for Amex).
- **Capture burst at draw close.** Many winners are captured at once. *→* ④'s
  concern; capture in an idempotent batch.
- **本人確認 depth.** MVP captures name + contact bound to the account (enough for
  covered-ticket status) — not マイナンバー-grade KYC. *→* Sufficient per roadmap;
  revisit if the identity tier (`face-auth-entry`) is pursued.

## Migration Plan

New capability; no existing behavior changes. Sequence when implementing: proto
(`LotterySalesPhase`, `TicketApplication` with the authorization ref, RPCs incl.
the draw's capture/cancel) → BSR → backend (phase config, apply + authorize, draw
job with capture/cancel, results) → frontend (apply flow with card authorization,
my-application/result views) → organizer console (phase config). ⑤ is still
required to turn a captured winner into an Order + Ticket; ④ can ship its
application/draw/capture surface and stub the ⑤ issuance handoff until ⑤ lands,
but a real, fulfilled sale is not complete until ⑤ ships.

## Open Questions

- **二次抽選** (a second draw over the leftover/waitlist) — the persisted waitlist
  supports it, but whether MVP exposes a second phase is deferred; does not
  change ④'s entities.
- **Capture ↔ issuance ordering** — ④ captures at the draw and ⑤ issues; the exact
  reconciliation (refund-on-issuance-failure, idempotency) is a ④/⑤ boundary
  detail to settle when ⑤ is specced. Does not change ④'s spec surface.
