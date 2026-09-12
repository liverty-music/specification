## Context

④ `lottery-application` is SHIPPED (spec v0.58.0 #887 / backend #426 / frontend
#577) with a Stripe manual-capture hold, authored to capture as a **destination
charge + `on_behalf_of`**. That topology settles funds to the Organizer at capture
and cannot back the hold-to-event escrow the ticketing scheme assumes; PR #936
reconciled ⑤ + `payments-design.md` to **separate charges & transfers**. This change
makes ④'s capture path match. Stripe KYC (task 0.1) is still open, so **no live
charge has run** — the switch is still free of migration cost. Full rationale +
competitor/Stripe grounding: `payments-design.md` "Why separate charges &
transfers". This design records only the ④-specific technical shape.

## Goals / Non-Goals

**Goals:**
- ④'s draw-capture creates a **platform-held separate charge** (funds on the
  platform balance); Organizer settlement deferred to a **post-event `Transfer`**.
- Platform is the Stripe settlement merchant (MoR) with a recognizable statement
  descriptor; Organizer stays the **legal seller-of-record** (特商法 表記).
- No behavior change to the hold-at-apply, JPY/Amex rule, draw, loser release,
  本人確認 binding, or the ④→⑤ handoff.

**Non-Goals:**
- ⑤'s Order/issuance/payout spec (already platform-held via #936); ⑦ resale legs.
- The 収納代行 counsel opinion (payments-design flag 1) — a launch gate, not this
  change's surface.
- Adopting `allocated_funds` now (JP-ineligible — see Decisions).

## Decisions

- **Capture topology = separate charge on the platform, `on_behalf_of` OMITTED.**
  Confirmed against Stripe docs: with plain separate charges (no `on_behalf_of`),
  the platform is the settlement merchant, the buyer sees the **platform's**
  descriptor, settlement is platform-country (JP/JPY), and the platform holds the
  funds. Adding `on_behalf_of` would flip the settlement merchant + descriptor +
  settlement country to the connected account — which we do **not** want (it
  re-introduces Organizer-settlement). The Organizer stays seller-of-record via the
  収納代行 contract + 特商法 表記, a **separate axis** from the Stripe settlement
  merchant.
- **Organizer settlement = post-event `Transfer`** (`source_transaction` = the
  capture's charge id), released after the event + dispute buffer. This is the same
  payout leg ⑤ specifies — **it MUST be owned in one place** (⑤'s payout
  controller), not double-implemented in ④. ④'s responsibility ends at the
  platform-held capture + handoff.
- **`allocated_funds` (funds segregation) NOT adopted now — JP is ineligible.**
  Stripe docs list only BE/CH/DE/DK/ES/FR/GB/NL/SE/US; **Japan is not a supported
  market**, and it is a **private preview** with no published JP timeline. Plain
  separate charges & transfers (funds sit in the general platform balance until the
  Transfer) is fully supported in JP and is the MVP mechanism. `allocated_funds`
  (which would isolate held funds from platform payouts / other refunds / fee
  draw-down) is a **Stripe-account-manager conversation**, tracked as an open item,
  not a dependency. (Docs imply single manual-capture is compatible — allocation
  happens at capture; only multicapture/overcapture/incremental-auth are excluded —
  but confirm when requesting access.)
- **Statement descriptor design (platform account, GA in JP).** Set once on the
  platform account: a Latin static **prefix** (2–10 chars, must be alphabetic, e.g.
  `LIVERTY`) + **kanji and kana** static prefixes so JP-issued Visa/Mastercard
  render native script. Per event, set `statement_descriptor_suffix` (Latin) and
  `payment_method_options[card][statement_descriptor_suffix_kanji|_kana]` with an
  abbreviated event/organizer name to cut "unrecognized charge" disputes. Budgets:
  Latin full 5–22 (network sees first 22 incl. `* ` separator; ~13 left after a
  7-char prefix); **kanji full 17**, kana full 22; no `< > \ ' " *` / full-width `＊`.
  Because **JCB/Diners/Discover show the account default during the pre-capture
  delay** (kanji/kana reach the issuer only at capture), the platform's **default
  descriptor must itself be recognizable**.
- **Negative-balance responsibility on the platform.** Chargebacks/refunds draw on
  the platform balance; the platform must be loss-liable for connected-account
  negative balances (`controller[losses][payments]=application` / Custom-equivalent)
  — the config that also unlocks `allocated_funds` later. Reserve past the dispute
  window; `transfer_reversal` claws back an already-transferred share.
- **No proto/BSR change expected.** The `Order`/`Payment` model is provider-agnostic
  (opaque `pi_`/`pm_`); charge topology is a backend/Stripe-config concern. Confirm
  no entity field encodes the destination-charge assumption before closing design.

## Risks / Trade-offs

- **Double-owned Transfer.** ④ and ⑤ both touch settlement. *→* ④ ends at
  platform-held capture + handoff; ⑤'s payout controller owns the post-event
  Transfer. Document the boundary in both.
- **④ may be stubbed or already-separate.** The shipped charge topology is unverified
  (Stripe KYC open). *→* Task 0: read the ④ backend capture path first; if it's
  stubbed or already a platform charge, this narrows to config + descriptor + a spec
  clarification.
- **Descriptor truncation on JP cards.** Kanji budget is only 17. *→* Abbreviate
  event names; keep the platform default recognizable for the JCB/Diners/Discover
  pre-capture window.
- **No fund isolation without `allocated_funds`.** Held funds mix with the general
  platform balance until Transfer. *→* Accept for MVP (all JP incumbents run this
  way); careful balance monitoring + reserve; revisit `allocated_funds` with Stripe
  if isolation becomes material.

## Open Questions

- **Stripe: JP availability + timeline for `allocated_funds`**, and confirmation
  that single manual-capture is supported under it (docs imply yes). Account-manager
  question — not answerable from docs.
- **Exact statement-descriptor strings** (platform default + prefix in Latin/kanji/
  kana; per-event suffix abbreviation scheme) — set with payment ops.
- **④'s actual shipped charge topology** (destination vs already-separate vs stubbed)
  — resolve in task 0 before scoping the backend delta.
