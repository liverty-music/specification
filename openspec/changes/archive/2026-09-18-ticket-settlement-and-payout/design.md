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
- **KYC/KYB identity is collected by Stripe, never by us.** `CreateConnectedAccount` sends
  the account *shape* — country, currency/locale, `dashboard = none`, the requested
  `stripe_transfers` capability, and the fees/losses collector responsibilities — plus the
  Organizer's business **contact email**, which Stripe requires whenever a recipient
  configuration is supplied ("If configuration.recipient is supplied, the Account must have
  a contact email"); it is sourced from the Organizer record, not collected anew. A JP
  recipient additionally needs `configuration.merchant.mcc`, without which the transfers
  capability never activates — declaring the MCC does not make the account
  merchant-of-record, since no merchant capabilities are requested. Beyond the contact
  email the request carries **no** personal data. The Organizer supplies their name, date of birth, address
  and documents directly to Stripe through the hosted onboarding link
  (`CreateOnboardingLink` → Stripe AccountLink), so no PII transits or rests in our systems
  and the platform's compliance surface stays minimal. The account is created in `Pending`
  and becomes payout-eligible only when Stripe reports the capability `active`.
  *Note for readers of the PoC test:* it passes a full hardcoded identity block only
  because an automated test cannot click through a hosted web page — that is a test
  shortcut, **not** a template for the production call.
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
  trodden JP path; multi-party splitting would raise the risk. *→* MVP single-payee; the
  counsel opinion (payments-design flag 1) gates launch and is tracked by
  `payments-legal-compliance` §1.1, not here. Multi-payee re-analysis before any venue
  payee.
- **Statement shows the platform, not the Organizer (no `on_behalf_of`).** The buyer's
  statement prefix is the platform brand. *→* Accepted: it is the JP-incumbent norm
  (Peatix/ZAIKO), the per-event suffix keeps it recognizable, and seller-of-record is
  carried contractually + in 特商法 表記. If counsel later requires the Organizer's name on
  the statement, that is a future change (merchant onboarding + pre-sale gating), not a flag
  flip — it changes the sales-gating model.
- **Every Stripe context is a sandbox; no livemode account is involved.** This matches how
  ④ `lottery-application` shipped and archived — prod-verified on Stripe **test mode**, with
  live-money items split out — and what `payments-legal-compliance` states: paid ticketing
  runs in test mode until its §4.1 launch gate lifts. Three contexts:
  - **local** / **ci** sandboxes — keyed from the shell/`.env` and the backend repo's
    `STRIPE_TEST_SECRET_KEY` Actions secret. Where the E2E harness runs.
  - **`pannpers.dev sandbox`** — the **preprod** account the `prod` Pulumi stack points at,
    keyed through Pulumi ESC → GSM → ESO. "prod" here means the prod deployment stack, not a
    livemode Stripe account.
  - **`dev`** — deliberately **no** Stripe key. `pulumiConfig.stripeSecretKey` is unset, so
    the backend runs `NoopAuthorizationPort` and the webhook handler fails closed (503).

  Two consequences. There is no dev webhook endpoint to register — the only registered
  endpoint is the prod stack's, in the preprod sandbox. And because that endpoint lives in a
  sandbox, registering it is **not** a launch-gated step: it can be done now, and prod
  test-mode verification is what this change archives on. The eventual livemode account is
  `payments-legal-compliance`'s concern, not this change's.
- **The prod webhook endpoint is registered from IaC, not the Dashboard.**
  `POST /v1/webhook_endpoints` returns the `whsec_…` signing secret in its creation response,
  so a Pulumi Dynamic Resource — the pattern already used in `src/zitadel/dynamic/` for APIs
  no provider covers — can hand it directly to the GSM secret that ESO syncs. That removes
  the manual copy of a credential between two consoles, and puts the subscribed event list
  under review in version control rather than in Dashboard state. Scoped to the prod stack:
  per the environment decision above there is no dev Stripe environment and therefore no dev
  endpoint.
- **No fund isolation (no `allocated_funds`).** Held funds mix with the general platform
  balance. *→* Careful balance monitoring + reserve; revisit with Stripe if JP opens.

## Migration Plan

New capability. Sequence: proto (connected-account ref/status, `SettlementSplit`, payout/
refund state, RPCs) → BSR → backend (Connect onboarding + KYC gate, payout controller with
`source_transaction` Transfers, refund executor + `transfer_reversal`, reserve, webhook
ingest) → cloud-provisioning (transfer/dispute webhook endpoint + signing secret) →
console (payout/refund ops). The Stripe-account-side config (loss-liable controller,
statement-descriptor prefix incl. kanji/kana) is a Dashboard/account item rather than
IaC: the loss-liable controller is already in place, the descriptor strings are still
open. Gated on ④ (charge) + ⑤ (Order). Launch is additionally gated on
`payments-legal-compliance`, which owns the 収納代行 counsel opinion and the livemode
Stripe 審査.

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
- **Whether Pulumi should hold a Stripe secret key, and whether the webhook endpoint's
  `delete` should really delete.** Registering the endpoint from IaC means the prod stack
  authenticates to Stripe with a payments credential, which widens what a compromised Pulumi
  run can reach. And a Dynamic Resource whose `delete` removes the endpoint lets a state
  change silently stop production webhook delivery — the dispute/refund path. Both are
  settled when 5.1 is implemented; a `delete` that only logs, or a restricted key scoped to
  webhook endpoints, are the obvious candidates.
- **Fee rate + buyer-pass-through** — business decision (#778).
