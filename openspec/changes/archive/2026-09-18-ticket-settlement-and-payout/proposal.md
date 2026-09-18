## Why

The ticketing money-**out** layer does not exist yet. Investigation of the shipped
code found: ④ `lottery-application` charges the fan with a **plain platform-account**
Stripe manual-capture `PaymentIntent` (no Connect, no `transfer_data`, no
`on_behalf_of`, no `application_fee`), so captured funds already sit on the
**platform balance** — but there is **no** organizer payout, no Stripe Connect
onboarding, no fee split, no refund/`transfer_reversal`, and no payout-hold anywhere
in the backend. ⑤ `ticket-purchase-and-issuance` covers issuance (Order + Ticket),
not the settlement of money to the Organizer. This change defines that settlement
layer: **hold buyer funds on the platform balance until the event, then `Transfer`
the Organizer's net share (platform keeps its fee), with refund/dispute clawback** —
i.e. **separate charges & transfers**, which is essential and currently unbuilt.

Payee model is **single Organizer + Liverty Music platform fee** (the venue is the
Organizer's cost, paid by the Organizer — the universal ticketing norm; ぴあ/ローチケ/
e+/Peatix/tiget/ZAIKO and DICE/AXS/Eventbrite all settle to one payee, and DICE's
T&Cs make the Vendor responsible for the venue fee). Payout is modelled as an
**extensible set of settlement splits** so a venue/artist payee can be added later
without a proto break, but the **MVP has exactly one split (the Organizer)**.
Rationale, competitor + Stripe grounding: [`payments-design.md`](../../../docs/payments-design.md).

## What Changes

- **Organizer Stripe Connect onboarding (Accounts v2 recipient).** Each Organizer gets a
  **v2 connected account provisioned as a payout recipient** — requesting only the
  **`transfers` capability on `stripe_balance`**, NOT `card_payments` (per Stripe's
  separate-charges guidance: requesting `card_payments` for a recipient is unnecessary and
  slows onboarding). A payout is **blocked until `recipient.capabilities.stripe_balance.
  stripe_transfers.status` is `active`**. The platform is **loss-liable** for
  connected-account negative balances (`losses_collector = application`) — required for
  separate charges & transfers and for transfer reversals during disputes.
- **Separate charges & transfers payout.** ④'s captured charge already lands on the
  **platform balance** (no ④ change needed). After the event + dispute buffer, a
  **scheduled platform process** creates a **`Transfer` (with `source_transaction`
  = the charge) to the Organizer's connected account** for the Organizer's net share;
  **Liverty Music keeps its platform fee by retaining the remainder** (no self-transfer).
- **Extensible settlement splits.** The payout is a set of **splits**; MVP = one
  Organizer split + the retained platform fee. The model admits N payees (venue,
  artist) later; adding one is onboarding + a split row, **not** a proto break.
- **Platform is the Stripe settlement merchant — NO `on_behalf_of` (MVP).** Per Stripe's
  Connect guidance, `on_behalf_of` is not used for standard separate-charges flows: naming
  the Organizer would require its connected account to hold the `card_payments` capability
  (active **before** the charge), which would gate ticket sale on full merchant KYB and
  contradict "onboarding never blocks sale." The Organizer stays the **seller-of-record
  contractually** (代理受領権限 + 特商法 表記), while the platform is the Stripe merchant.
  The buyer's statement stays recognizable via the **platform static prefix + a per-event
  dynamic suffix** (Latin + JP kanji/kana) — achievable without `on_behalf_of`. Making the
  Organizer the Stripe MoR (Organizer-named statement) is deferred to a **future change**
  (merchant onboarding + pre-sale gating), if counsel later requires it.
- **Hold-to-event + dispute-buffer release gate.** No payout before the event's
  `start_time` has passed AND a dispute-safety window; **postponement resets** the
  clock to the new date. This is the escrow-with-counter-performance gate that
  supports the 収納代行 characterization.
- **Refund / dispute execution mechanics (RPC entry stays in ⑤).** ⑤'s
  `OrderAdminService.RefundOrder` (already merged in #938) is the admin refund entry
  point; this capability provides the **money movement it invokes** — `Refund` from the
  **platform balance** + **`transfer_reversal` per split** + reserve past the dispute
  window — and handles the inbound Stripe **refund/dispute webhooks**. ⑤ owns the
  policy + RPC; settlement moves the money. This capability does **NOT** redefine
  `RefundOrder`/`Order`/`Ticket` (no change to #938's proto).
- **`allocated_funds` (funds segregation) NOT adopted** — JP is not an eligible market
  (private preview: BE/CH/DE/DK/ES/FR/GB/NL/SE/US; a preview header does not unlock
  it). MVP holds funds in the general platform balance until Transfer; JP access is a
  Stripe-account-manager item.

## Capabilities

### New Capabilities
- `ticket-settlement-and-payout`: Organizer Connect onboarding (v2 recipient, transfers
  capability); hold-to-event separate-charges-&-transfers payout (single-Organizer split +
  retained platform fee, extensible to N payees); platform-MoR statement descriptor
  (platform prefix + per-event suffix, no `on_behalf_of`); contractual seller-of-record;
  refund/dispute `transfer_reversal` execution; negative-balance responsibility — under the
  収納代行 scheme.

### Modified Capabilities
<!-- none — ④'s charge is unchanged (already platform-held). ⑤'s Order/Ticket/
     issuance/RefundOrder proto is already merged (#938) and is NOT modified here;
     this capability is purely additive (onboarding + payout job + split + config +
     the transfer_reversal mechanics behind ⑤'s RefundOrder). ⑤'s change-doc payout
     wording is trimmed as a coherence edit, not a delta against a synced main spec. -->

## Impact

- **Note — ⑤ proto already merged (#938).** `Order`/`Ticket`/`Payment` (OrderStatus
  paid/refunded/failed, opaque `pi_`/`pm_`), `IssuanceService.IssueFromCapturedWin`, and
  `OrderAdminService.RefundOrder` (refund + transfer_reversal) are on main. This
  capability adds the **missing** surface only (Connect onboarding, payout, splits) and
  supplies the money-movement behind `RefundOrder`; it does **not** touch #938's files.

- **Backend (new):** Connect onboarding (create connected account, KYC status gate),
  a payout controller (post-event `Transfer` per split, `source_transaction`), refund
  executor (`Refund` + per-split `transfer_reversal`), reserve handling. All new — no
  ④ charge change (④'s plain platform charge already funds this).
- **Proto/BSR:** a settlement/payout surface — Organizer connected-account ref +
  recipient/transfers status, a `SettlementSplit` model (payee ref + amount/share), and
  payout/refund state including the **captured-charge ref (`ch_`)** resolved for
  `source_transaction`. Provider-agnostic (opaque Stripe refs). Confirm shape in design.
- **cloud-provisioning:** webhook endpoint + signing secret for transfer/payout/dispute
  events. The Stripe-account-side config (loss-liable controller, statement-descriptor
  prefix incl. kanji/kana) is a Dashboard/account item rather than IaC.
- **Depends on:** ④ (the captured platform charge) + ⑤ (the Order the payout settles
  against). **Gates launch** (first live paid sale) together with
  `payments-legal-compliance`, which owns the 収納代行 counsel opinion and the livemode
  Stripe 審査; the test-mode Connect platform + recipient config is already in place.
- **Relationship to ⑤:** ⑤ owns Order/Ticket issuance + the refund *policy*
  (cancellation/postponement); this capability owns the *money movement* (payout,
  refund execution, reversal). The former "④ destination-charge follow-up" is
  **withdrawn** — its premise (④ used a destination charge) was factually wrong.
