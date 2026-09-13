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
  **`source_transaction` needs the charge id (`ch_`), which ⑤'s `Payment` stores only as a
  PaymentIntent ref (`pi_`).** The payout job therefore resolves `pi_` → `ch_` at Transfer
  time (retrieve the PaymentIntent with `latest_charge` expanded) and records the `ch_` on
  the settlement/payout row so the reversal path reuses it.
- **No `on_behalf_of` — the platform is the Stripe settlement merchant (MVP).** Stripe's
  Connect guidance lists `on_behalf_of` as a trap for standard separate-charges flows, and
  the mechanics confirm why: to put the Organizer's name on the statement, `on_behalf_of`
  requires the Organizer's connected account to hold the **`card_payments` capability**
  ("連結アカウントから静的コンポーネントを使用するには card_payments ケイパビリティが必要"),
  and that capability must be **active before the charge is created** — i.e. before the
  lottery authorization at application time. That would gate ticket sale on full merchant
  KYB, directly contradicting "onboarding never blocks sale," and would force a heavier
  merchant account instead of a lightweight `transfers`-only recipient. The three axes stay
  separate but decoupled from the Stripe flag: **seller-of-record = Organizer (contractual:
  代理受領権限 + 特商法 表記), money-handling = platform 収納代行 agent, Stripe settlement
  merchant = the platform (no on_behalf_of).** Dropping `on_behalf_of` costs only the
  statement *prefix name* (platform vs Organizer); recognizability, kanji/kana, chargeback
  liability (platform under either model), and all transfer mechanics are unchanged. This
  matches the JP incumbents cited elsewhere (Peatix/ZAIKO show the platform on the statement
  and operate as 収納代行). Organizer-named statement (on_behalf_of + merchant onboarding +
  pre-sale gating) is a **future change** if counsel requires it.
- **Statement descriptor (platform account).** Platform static prefix (Latin 2–10, +
  kanji/kana on the **platform** account) + a per-event `statement_descriptor_suffix`
  (+ `payment_method_options.card.statement_descriptor_suffix_kanji`/`_kana`) set on the
  charge — all without `on_behalf_of`, since the platform is the settlement merchant.
  Budgets: Latin total 22, kanji 17, kana 22; no `< > \ ' " *`. JCB/Diners/Discover show
  the account default during the pre-capture window, so the platform default must itself be
  recognizable. NOTE: the per-event suffix is a charge-creation-time param (④); the MVP may
  ship with the platform static descriptor alone and add the suffix as a small, optional ④
  enhancement — it is independent of this capability's Transfer logic.
- **Accounts v2 recipient / loss-liable / negative-balance responsibility on the platform.**
  Organizer accounts are created via **Accounts v2** as **payout recipients** — requesting
  the **`transfers` capability on `stripe_balance`** only, NOT `card_payments` (unnecessary
  for a recipient and slows onboarding). `losses_collector = application` (platform absorbs
  negative balances) — required for separate charges & transfers, transfer reversals, and
  any future `allocated_funds`. Payout eligibility gate =
  `recipient.capabilities.stripe_balance.stripe_transfers.status == "active"` (v2 capability
  status, NOT the deprecated v1 `payouts_enabled`). Refunds/disputes debit the platform
  balance; reserve past the dispute window; `transfer_reversal` per split claws back
  transferred shares.
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
- **Statement shows the platform, not the Organizer (no `on_behalf_of`).** The buyer's
  statement prefix is the platform brand. *→* Accepted: it is the JP-incumbent norm
  (Peatix/ZAIKO), the per-event suffix keeps it recognizable, and seller-of-record is
  carried contractually + in 特商法 表記. If counsel later requires the Organizer's name on
  the statement, that is a future change (merchant onboarding + pre-sale gating), not a flag
  flip — it changes the sales-gating model.
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

- **Organizer-named statement (future `on_behalf_of` change)** — MVP is decided as
  platform-MoR (no on_behalf_of). Only if counsel requires the Organizer's name on the
  buyer's statement does this reopen — as a separate change (merchant onboarding +
  card_payments + pre-sale gating), with the tax/settlement-country implications assessed
  then.
- **Exact dispute-buffer / release length** — tunable op parameter (the gate, not the
  duration, is load-bearing).
- **`allocated_funds` JP availability + manual-capture support** — Stripe account-manager
  question (not answerable from docs).
- **Fee rate + buyer-pass-through** — business decision (#778).
