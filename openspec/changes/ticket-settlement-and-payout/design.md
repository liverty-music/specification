## Context

Money-**out** layer for the ticketing platform. Grounded in a read of the shipped
backend: ④ `lottery-application` charges via a **plain platform-account** manual-capture
`PaymentIntent` (`internal/infrastructure/payment/stripe_authorization.go` — no
`TransferData`/`OnBehalfOf`/`ApplicationFee`), so funds already land on the **platform
balance**. There is **no** Connect onboarding, Transfer, payout, refund, or
`transfer_reversal` anywhere in the backend, and no `Order`/settlement proto. ⑤
`ticket-purchase-and-issuance` covers Order/Ticket issuance, not settlement. This change
adds the settlement/payout layer. Money design + competitor/Stripe grounding:
[`payments-design.md`](../../../docs/payments-design.md).

**⑤ proto already merged (#938).** `Order`/`Ticket`/`Payment` (OrderStatus
paid/refunded/failed; opaque `pi_`/`pm_`), `IssuanceService.IssueFromCapturedWin`, and
`OrderAdminService.RefundOrder` (refund + transfer_reversal, with a `RefundReason` enum
for cancellation/postponement/dispute) are on main. This capability is **purely
additive** — it defines the missing onboarding/payout/split surface and supplies the
money-movement behind `RefundOrder`; it does **not** modify #938's proto, and the refund
**RPC entry** stays in ⑤.

## Goals / Non-Goals

**Goals:**
- Hold buyer funds on the platform balance until the event, then Transfer the
  Organizer's net share (platform retains fee) — separate charges & transfers.
- **Single-Organizer payee + platform fee**, modelled as extensible splits.
- Organizer Connect onboarding + KYC gate; refund/dispute clawback; hold-to-event gate.

**Non-Goals:**
- ④'s charge (unchanged — already platform-held) and ⑤'s Order/Ticket issuance.
- **Venue/artist as direct payees** (deferred; venue is the Organizer's cost — industry
  norm). The splits model leaves room, but no venue onboarding is built now.
- `allocated_funds` fund isolation (JP-ineligible; Stripe-contact item).
- ⑦ resale's seller-refund leg (different timing/theory).

## Decisions

- **Single-Organizer payee + platform fee (extensible splits).** Verified against
  competitors: **every** JP incumbent (ぴあ/ローチケ/e+/Peatix/tiget/ZAIKO) and global
  (Eventbrite/DICE/AXS/Universe) settles to **one payee** (the organizer/promoter/
  vendor); the venue is the Organizer's cost (DICE's T&Cs make the Vendor pay the venue
  fee). Only Ticket Fairy offers a multi-party "Split Settlement", as an enterprise
  exception. So MVP = one Organizer split; model it as a set of splits so a venue/artist
  payee is a later onboarding + split row, not a proto break.
- **④'s plain platform charge is the funding source — no ④ change.** The earlier
  "④ shipped a destination charge → migrate to separate charges & transfers" premise was
  **factually wrong** (confirmed by reading the code). ④'s charge already lands on the
  platform balance, which is exactly the "charge" half of separate charges & transfers.
  This capability adds the missing "transfers" half.
- **Payout = `Transfer` with `source_transaction` = charge; platform fee = retained
  remainder.** Per Stripe docs, multiple transfers may reference one charge via
  `source_transaction` as long as their total ≤ the charge; the transfer waits until the
  charge's funds are available. Liverty Music keeps its fee simply by **not** transferring it
  (no self-transfer). `source_transaction` is set at creation and cannot be updated.
- **`on_behalf_of` = the Organizer (single seller-of-record).** `on_behalf_of` names
  exactly one account and sets the settlement merchant / statement descriptor / settlement
  country — so it must be the Organizer. The platform stays the 収納代行 agent + holds
  funds; the three axes (seller-of-record = Organizer, money-handling = platform agent,
  Stripe MoR here = Organizer via on_behalf_of) are kept explicit. *(Trade-off: with
  on_behalf_of the descriptor/settlement follow the Organizer; without it the platform is
  MoR. For a single Organizer seller-of-record, on_behalf_of = Organizer is the cleaner
  fit and matches "the Organizer sells the ticket." Revisit if the platform must be MoR.)*
- **Statement descriptor.** Platform static prefix (Latin 2–10, + kanji/kana on the
  platform account) + per-event `statement_descriptor_suffix` (+ `_kanji`/`_kana`)
  naming the event/organizer. Budgets: Latin total 22, kanji 17, kana 22; no
  `< > \ ' " *`. JCB/Diners/Discover show the account default during the pre-capture
  window, so the default must itself be recognizable.
- **Loss-liable controller / negative-balance responsibility on the platform.** Required
  for separate charges & transfers and for any future `allocated_funds`. Refunds/disputes
  debit the platform balance; reserve past the dispute window; `transfer_reversal` per
  split claws back transferred shares.
- **`allocated_funds` NOT adopted — JP ineligible.** Three gates (preview header opt-in;
  private-preview access grant; market eligibility) and JP is not in the market list
  (BE/CH/DE/DK/ES/FR/GB/NL/SE/US). Held funds sit in the general platform balance until
  Transfer (the JP-incumbent norm). Track JP access as a Stripe-account-manager item.
- **Refund ownership split with ⑤.** ⑤ owns the refund *policy* (cancellation refunds the
  current holder; postponement offers a bounded window; issuance-failure → refund). This
  capability owns the *execution* (Refund + per-split transfer_reversal + reserve +
  idempotent webhooks). Keeps ⑤ focused on ticket lifecycle, this on money movement.
- **Provider-agnostic surface.** Connected-account ref + status, `SettlementSplit`
  (payee ref + amount/share), payout/refund state — opaque Stripe refs, own enums, no raw
  provider status. Keeps a KOMOJU/Adyen switch a schema-stable adapter change.

## Risks / Trade-offs

- **Organizer KYC stalls block payout.** *→* Payout waits (doesn't fail); surface
  onboarding status to organizers; sales/issuance unaffected.
- **Chargeback after payout.** *→* Reserve past the dispute window + platform
  negative-balance responsibility + `transfer_reversal`.
- **JP 資金移動業 / 収納代行 boundary.** Single-payee collection-agent is the lower-risk,
  trodden JP path; multi-party splitting would raise the risk. *→* MVP single-payee;
  counsel opinion (payments-design flag 1) gates launch. Multi-payee re-analysis before
  any venue payee.
- **`on_behalf_of` vs platform-MoR.** Choosing Organizer-as-MoR ties descriptor/
  settlement to the Organizer's connected account; if the platform later needs to be MoR
  (e.g. for a unified descriptor), that flips. *→* Decide with payment ops; both are
  supported by the same separate-charges topology.
- **No fund isolation (no `allocated_funds`).** Held funds mix with the general platform
  balance. *→* Careful balance monitoring + reserve; revisit with Stripe if JP opens.

## Migration Plan

New capability. Sequence: proto (connected-account ref/status, `SettlementSplit`, payout/
refund state, RPCs) → BSR → backend (Connect onboarding + KYC gate, payout controller with
`source_transaction` Transfers, refund executor + `transfer_reversal`, reserve, webhook
ingest) → cloud-provisioning (Stripe Connect platform config: loss-liable controller,
descriptor prefix incl. kanji/kana, transfer/dispute webhooks) → console (payout/refund
ops). Gated on ④ (charge) + ⑤ (Order). Long-lead externals (Stripe KYC, 収納代行 counsel)
gate launch.

## Open Questions

- **`on_behalf_of` = Organizer vs platform-MoR** — final call with payment ops/counsel
  (statement-descriptor + settlement-country + tax implications).
- **Exact dispute-buffer / release length** — tunable op parameter (the gate, not the
  duration, is load-bearing).
- **`allocated_funds` JP availability + manual-capture support** — Stripe account-manager
  question (not answerable from docs).
- **Fee rate + buyer-pass-through** — business decision (#778).
