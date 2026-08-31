## Why

A fan who buys a ticket and then cannot attend has no sanctioned way to hand it
on. Ad-hoc refunds do not scale and person-to-person resale is both a scalping
loophole and a legal hazard (為替取引 / 資金移動業, 不正転売禁止法, 古物営業法).
The JP market default — reinforced after チケトレ shut down 2025-06-30 — is that
each primary platform runs its **own official, face-value resale on its own
issuance base**. Liverty issues its own account-bound tickets, so it is exactly
positioned to offer this. Official face-value resale is the anti-scalp gold
standard (ローチケ/ぴあ), the legally favored path, and a real day-one need
("the buyer got sick").

The full legal + competitor research and the settled design decisions are
captured in [`docs/resale-design.md`](../../../docs/resale-design.md); this
change turns that design into a specced capability.

## What Changes

- Introduce **official, face-value ticket resale** as a sanctioned safety valve
  for the cannot-attend case, structured as **two decoupled money legs** — a
  refund of the seller's own purchase + a fresh face-value sale to a new buyer —
  so **money never moves individual-to-individual** (payee is always the
  business Organizer; keeps the platform a 収納代行, not a 資金移動業).
- A ticket **owner** can **list** a PAID, unused ticket for resale before the
  deadline (`start_time − 1h`) and **withdraw** it any time before it matches.
- Resale inventory is a **public marketplace** (any buyer can discover + join),
  but matching is **priority-ordered — lottery-losers first, then general public**
  — via **sequential timed offers**, not first-come.
- On a match, atomically: settle the buyer's fresh face-value payment, **void**
  the seller's original ticket, and **issue a new ticket** to the buyer with
  **本人確認 re-bound** (preserving 特定興行入場券 status).
- The seller's refund (original payment **minus a ~10% resale fee**) is
  **triggered on resale completion with a short hold-back reserve — NOT held to
  the event** (matches ぴあ/ticket board/e+/tiget). The **buyer pays exactly face
  value** (券面代金; the original booking fee is excluded and non-refundable).
- A **返品特約 (no-return clause)** is shown on the buyer's final confirmation
  screen (特商法 §12-6), distinct from fee disclosure; the fee is framed as
  役務提供の対価.
- Resale is **mandatory-by-default** on every standard paid event via blanket
  Organizer consent in the platform agreement; non-resellable only via automatic
  **structural exclusions** (free/¥0, comp, goods-bundled, name-locked) or a
  rare admin exception. **No organizer self-serve off-switch.**
- **Sales precondition:** ticket sales/resale require the event's mandatory info
  (including `start_time`) to be set, so the `start_time − 1h` deadline is
  computable.
- Event **cancellation** while a ticket is listed routes to the normal
  cancellation-refund path; **postponement** recomputes the deadline and keeps
  listings/settled resales valid.
- **Unsold at deadline = return-only** (no organizer buyback in MVP). **Match
  notification** (push/email) is a **future** enhancement.

Scope guardrails (MVP): electronic tickets only (no physical inventory →
license-exempt); anonymous pool (no P2P contact); no above-face pricing; no
buyer-side markup. Provider/payment mechanics reuse ⑤'s Stripe Connect /
収納代行 scheme unchanged.

## Capabilities

### New Capabilities
- `official-resale`: face-value resale of an issued ticket — listing lifecycle,
  the public marketplace + loser-priority sequential timed matching, the two-leg
  money model (seller refund on resale completion + fresh face-value buyer sale),
  mandatory-by-default enablement with structural exclusions, buyer 返品特約, and
  the covered-ticket (特定興行入場券) re-bind on reissue.

### Modified Capabilities
<!-- None yet. official-resale reuses the Order/Payment/Ticket entities defined by
     the not-yet-specced ⑤ ticket-purchase-and-issuance and ⑥ ticket-wallet-and-
     checkin, and the demand pool from ④ lottery-application. Those are DEPENDENCIES
     (see design.md), not modifications of existing shipped specs. When ⑤/⑥ are
     specced, this change may add delta modifications to their ticket lifecycle;
     for now the resale capability is self-contained. -->

## Impact

- **Depends on (not yet specced/built):** ④ `lottery-application` (the
  loser demand pool), ⑤ `ticket-purchase-and-issuance` (Order/Payment/Ticket +
  収納代行 + refunds), ⑥ `ticket-wallet-and-checkin` (issue / void / rotating-QR
  / 本人確認 binding). This change is **authored ahead** to lock the design; its
  `tasks.md` is gated on ④⑤⑥ shipping first.
- **New domain entity:** `ResaleListing` (references the seller's original
  `Payment` and the buyer's new `Order` — no new money primitive).
- **New RPCs:** seller `ListForResale` / `WithdrawListing`; buyer join-queue +
  match→buy; organizer/admin structural-exclusion + earlier-cutoff config.
- **Payments (⑤):** reuses Stripe Connect / 収納代行; adds the seller-refund
  trigger on resale completion (with a hold-back reserve) and `transfer_reversal`
  clawback for chargebacks. Legal counsel brief (9 items) folded into #778.
- **Legal:** confirms the two-leg structure avoids 資金移動業; no-inventory
  electronic resale avoids 古物商許可; blanket consent satisfies 不正転売禁止法.
- **No proto/frontend impact until ④⑤⑥ land;** this is a spec-only artifact now.
