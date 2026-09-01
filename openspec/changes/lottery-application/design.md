## Context

See [proposal.md](./proposal.md) for motivation. ④ is the first ticketing
capability; it owns the **application + draw** half of a lottery sale and hands
off to ⑤ `ticket-purchase-and-issuance` for the charge/Order/Ticket. Money
design + legal scheme: [`payments-design.md`](../../../docs/payments-design.md)
(#778). Depends on ② `organizer-event-authoring` (shipped) for the **published
Event** it attaches a phase to. **Note (existing-model reality):** neither ② nor
the Event/Venue proto exposes a **capacity** field, so ④ does **not** read a venue
capacity — the **Organizer sets the phase capacity** (sized to the venue by their
own knowledge). Publish/visibility state lives on the **concert/Series**, not the
Event, so ④ gates on the concert being `PUBLISHED`. ⑤/⑥ are not yet specced, so
the handoff shape here is a forward contract.

## Goals / Non-Goals

**Goals:**
- A correct, oversell-free lottery: draw against a **fixed capacity after
  applications close** (no real-time inventory race).
- Anti-scalp from day one: **1 account / 1 application** + **本人確認**.
- A clean ④/⑤ boundary and a **persisted loser draw order** that 繰上げ, 二次抽選,
  and ⑦ official-resale all reuse.

**Non-Goals (design-level):**
- FCFS/real-time sales, **seat maps, preference ordering**, multiple parallel
  pools — deferred (roadmap Guiding Decisions).
- The **charge**, Order, Ticket issuance, refunds — all ⑤.
- Companion ticket **distribution** — none; same-time entry is ⑥.

## Decisions

- **D-A — Card saved at application (SetupIntent), winners auto-charged at draw
  (user-confirmed).** At apply, capture + save the payment method via a Stripe
  `SetupIntent` (`usage=off_session`, 3DS once, **no auth hold**); at the draw,
  ⑤ charges winners **off-session** using the saved method. Rejected (Model B:
  no card at apply, winners actively pay post-draw) — it drops the frictionless
  auto-charge the JP incumbents (ぴあ/ローチケ) use and risks winner abandonment.
  Cost: ④'s application flow includes the Stripe card-capture touchpoint (thin —
  capture + store token only; the charge is ⑤).
- **Draw unit = the whole application (all-or-nothing).** A winning application
  wins **all** its requested tickets so companion groups stay intact; capacity is
  counted in **tickets**. Rejected: drawing individual tickets (would split
  groups).
- **Draw algorithm = random order + greedy fit.** Shuffle applications uniformly
  at random; admit each application whose ticket count **fits the remaining
  capacity**, waitlist the rest **in that same random order**; continue past a
  too-large application so smaller later ones can still fill capacity (better
  utilization than stop-at-first-exceed). Minor caveat: near-full capacity a
  larger group is marginally likelier to be skipped — accepted for MVP; capacity
  is never oversold.
- **Persisted ordered loser waitlist — of losing applications (per account).**
  The random draw order of non-winning **applications** is stored (each is one
  account's companion group). It is the single source for **繰上げ**, **二次抽選**,
  and ⑦ official-resale's demand pool. **Projection for ⑦:** a losing application
  maps to **one demand candidate (that account)** in draw order — ⑦'s per-seat
  offer queue derives candidates from this application ordering (not one entry per
  requested ticket). This is the "lottery-losers in draw order" ⑦ depends on; the
  timestamp-order fallback in ⑦'s older draft is superseded (④ always persists the
  random order — do NOT use timestamp order, it would be FCFS-unfair).
- **Payment-deadline clock owned by ④.** ④ sets and watches the deadline; ⑤
  reports charge outcome (succeeded/failed/needs-re-auth) but does NOT own the
  timer. Before the deadline, a failed / needs-re-auth outcome gets a **grace +
  re-auth link** (3DS step-up recovery); only a lapsed deadline voids the win.
  This resolves the "who owns the timer" ambiguity and matches payments-design's
  winner-charge-failure flow.
- **1 account / 1 application per phase**, withdrawable before the draw; a winner
  may decline pre-charge (→ 繰上げ); an issued ticket is not ④-withdrawable (→ ⑦).
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
- **④/⑤ boundary.** ④ owns: `LotterySalesPhase`, `TicketApplication` (incl. the
  saved `payment_method` token + 本人確認), the draw, win/loss, the **payment
  deadline + its timer**, and running 繰上げ. ⑤ owns: the off-session charge,
  Order, Ticket issuance, refunds, and **reporting** the charge outcome. The
  contract is "win → (⑤ charge; may need re-auth within grace) → issued | lapsed →
  繰上げ".

## Risks / Trade-offs

- **Authored partly ahead of ⑤.** The win→charge→issue handoff and the
  charge-failure signal are a forward contract; shapes may need reconciliation
  when ⑤ is specced. *→* Keep `TicketApplication` referencing (not defining)
  Order/Payment/Ticket; express the handoff as an application state + signal, not
  ⑤'s internals.
- **SetupIntent pulls Stripe into ④'s frontend.** *→* Keep it thin (Stripe
  Elements card capture + SetupIntent confirm + store `pm_`/`customer` refs);
  the heavy charge/refund logic stays in ⑤. Long-lead Stripe KYC / 収納代行
  counsel (#778) should already be in flight.
- **Draw fairness vs capacity utilization.** *→* Random order + greedy fit,
  documented; the skip-large caveat is accepted for MVP (small groups dominate).
- **Auto-charge timing = a burst at draw close.** ⑤ charges many winners at once.
  *→* ⑤'s concern (batch idempotency); ④ just emits wins.
- **本人確認 depth.** MVP captures name + contact bound to the account (enough for
  covered-ticket status) — not マイナンバー-grade KYC. *→* Sufficient per roadmap;
  revisit if the identity tier (`face-auth-entry`) is pursued.

## Migration Plan

New capability; no existing behavior changes. Sequence when implementing: proto
(`LotterySalesPhase`, `TicketApplication`, RPCs) → BSR → backend (phase config,
apply + SetupIntent, draw job, results, 繰上げ on ⑤ signal) → frontend (apply
flow with card capture, my-application/result views) → organizer console (phase
config). Depends on ⑤ for the end-to-end charge; ④ can ship its
application/draw surface and stub the handoff until ⑤ lands, but a real sale is
not complete until ⑤ ships.

## Open Questions

- **Draw scheduling mechanism** (cron job vs queue-triggered at close) — an
  implementation detail that does not change the spec surface.
- **二次抽選** (a second draw over the leftover/waitlist) — the persisted waitlist
  supports it, but whether MVP exposes a second phase is deferred; does not
  change ④'s entities.
