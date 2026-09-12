## Purpose

This capability turns a **captured** lottery win into an Order and issued tickets:
④ **authorizes (holds) the card at application and captures the winner's
authorization at the draw**; ⑤ takes that **captured winning payment** and records
an Order + issues Web2 account-bound tickets — under the 収納代行 scheme with the
Organizer as seller-of-record. It is the primary Order + issuance pipeline for the
ticketing MVP.

## ADDED Requirements

### Requirement: Issue from ④'s captured winning payment

The charge is performed by **④** (a Stripe **manual-capture** authorization held at
application and **captured at the draw** for winners, JPY card only). The captured
funds are **held on the platform balance** (separate charges & transfers) under the
収納代行 scheme — the platform later transfers the Organizer's net share (see
"Payout held to event"). **④ owns the PaymentIntent lifecycle and its provider
webhooks (authorize / capture / cancel)**;
on a successful capture ④ marks the application **Won-captured**. **⑤ is triggered
by ④'s confirmed-captured signal (the Won-captured application), NOT by a
⑤-owned capture webhook** (in the MVP the handoff is ④'s Won-captured record, not
an event). On that signal ⑤ SHALL create the **Order** referencing ④'s captured
PaymentIntent and proceed to issuance. ⑤ SHALL **NOT** perform a separate
off-session charge; there is **no ⑤-side payment deadline, off-session charge,
re-auth, or 繰上げ** — the hold-and-capture model removes them (④ releases losers'
holds; a capture that never succeeds leaves the seat unfilled for ④'s manual
follow-up).

#### Scenario: Order created from the captured winning payment

- **WHEN** ④ marks a winning application Won-captured (its held authorization captured at the draw)
- **THEN** ⑤ creates an Order referencing that captured PaymentIntent and proceeds to issuance

#### Scenario: ⑤ performs no separate charge and does not own the capture webhook

- **WHEN** a winner is being processed
- **THEN** ⑤ does not run an off-session charge / SetupIntent / payment-deadline / 繰上げ flow, and does not depend on a ⑤-owned capture webhook — the charge, capture, and its webhooks are ④'s; ⑤ keys on the Won-captured signal

#### Scenario: No Won-captured, no Order

- **WHEN** an application is not Won-captured by ④ (lost, or its capture never succeeded)
- **THEN** ⑤ creates no Order and issues no ticket (no ⑤-side retry/繰上げ)

### Requirement: Order record

The system SHALL create an **`Order`** for each purchase that is **provider- and
method-agnostic**: it stores opaque provider references (e.g. `pi_`/`pm_`), its
own `status` (**`paid`** on creation — the Order is created from an already-captured
payment — then `refunded`, or `failed` for the capture-succeeded-but-issuance-
refunded edge), `amount`+`currency`, `paid_at` (= the capture time), and optional
display facets (card brand/last4) — **never** PAN, CVC, or expiry. There is **no
`pending` Order** (the pre-capture authorize/hold state lives on ④'s
`TicketApplication`, not on ⑤'s Order). One Order SHALL cover the **N tickets** of
the winning application.

#### Scenario: Order is created already paid, referencing the captured payment

- **WHEN** an Order is created from ④'s captured winning payment
- **THEN** its status is `paid` with `paid_at` = the capture time, it stores only opaque provider token references, and never stores PAN/CVC/expiry

#### Scenario: One Order spans the companion group

- **WHEN** a winning application for N tickets is captured
- **THEN** a single Order covers all N tickets

### Requirement: Issue account-bound covered tickets on the captured win

On ④'s **Won-captured** signal the system SHALL issue **N account-bound Tickets**.
Each SHALL be a **covered ticket (特定興行入場券)** carrying **all three** legal
conditions: (i) the face states **resale without organizer consent is prohibited**,
(ii) the face specifies **date/venue + eligible-person** (the lottery is a common
pool with **no seat map** — the eligible-person is the bound holder, seat is
general-admission/none), and (iii) the **本人確認** is captured and noted on the
face, bound to the buyer's account. **本人確認 source depends on the phase's
verification requirement:** where the phase **required identity verification**
(identity-ekyc), the **verified identity is authoritative** and the bound name
MUST match the verified 本人確認 (no conflicting self-declared name); otherwise ④'s
**self-declared name + contact** is bound. Tickets MUST NOT be issued on a
client-side confirmation alone (issuance keys on ④'s captured-win signal).

#### Scenario: Tickets issued on the captured win

- **WHEN** ④ marks a winning application Won-captured
- **THEN** N account-bound covered tickets are issued to the buyer

#### Scenario: Issued ticket carries all three covered-ticket conditions

- **WHEN** a ticket is issued
- **THEN** its face states resale-without-consent is prohibited, specifies date/venue + eligible-person, and records the holder's 本人確認 (so it qualifies as a 特定興行入場券)

#### Scenario: Verified identity binds the covered ticket where required

- **WHEN** the phase required identity verification and a verified person's win is issued
- **THEN** the covered-ticket 本人確認 is the verified identity (a conflicting self-declared name is not bound)

#### Scenario: No issuance without the captured-win signal

- **WHEN** no ④ Won-captured signal exists for an application
- **THEN** no ticket is issued

### Requirement: Idempotent issuance; ⑤ owns refund/dispute webhooks

**Capture** and its provider webhooks belong to ④. ⑤ SHALL make **issuance
idempotent**: replaying the Won-captured signal (or retrying issuance) MUST NOT
double-issue tickets or double-create an Order for the same application. ⑤ SHALL
own the **refund and dispute** provider webhooks (from its own refund calls),
verify their signatures, and process them idempotently (no double-refund).

#### Scenario: Replayed captured-win signal issues exactly once

- **WHEN** ④'s Won-captured signal for an application is observed/retried more than once
- **THEN** the Order is created once and tickets are issued exactly once

#### Scenario: Refund webhook is idempotent

- **WHEN** a refund/dispute webhook (from ⑤'s refund) is delivered more than once
- **THEN** the refund is recorded once (no double-refund)

### Requirement: Capture succeeded but issuance failed

If ④'s capture **succeeded** but ⑤ **cannot complete issuance** (e.g. a persistence
error after capture), ⑤ MUST NOT leave money captured with no ticket. ⑤ SHALL
**retry issuance idempotently**; if issuance still cannot complete within a bounded
window it SHALL **refund/void the captured payment** (release the funds via
`Refund` + `transfer_reversal`) and surface the case for operator follow-up. It
MUST never double-issue on a later retry.

#### Scenario: Post-capture issuance failure is reconciled

- **WHEN** the capture succeeded but ticket issuance fails
- **THEN** ⑤ retries issuance idempotently, and if it still cannot complete it refunds the captured payment and flags the case (money is never captured with no ticket, and no double issuance occurs)

<!-- The former "Charge outcome reporting (grace before void)" requirement is
     REMOVED: ④'s authorization-hold model (authorize at apply, capture on win,
     release on loss) has no off-session charge, no payment deadline, no
     re-auth/grace, and no 繰上げ — a held authorization captured at the draw
     effectively does not fail; a rare failed capture is ④'s manual-follow-up
     concern (see "Issue from ④'s captured winning payment"). -->

### Requirement: Payout held to event plus dispute buffer

Buyer funds SHALL be **held on the platform balance** (separate charges &
transfers — **not** a destination charge, which would settle to the Organizer at
capture) and the Organizer's net share SHALL be **transferred** by a **scheduled
platform process** (not the Organizer) only after **the event's occurrence AND a
dispute-safety window**. "The event has occurred" SHALL be defined as **the
event's `start_time` (of its currently-scheduled date) having passed**; on a
**postponement (延期)** the release clock SHALL **reset to the new date** (never
release on a stale original date). The held platform balance funds this under the
収納代行 scheme.

#### Scenario: Payout not released before the event + buffer

- **WHEN** the event's current start_time has not passed, or the dispute buffer has not elapsed
- **THEN** the Organizer payout for that sale is not released

#### Scenario: Postponement resets the release clock

- **WHEN** an event is postponed to a later date
- **THEN** the payout release is re-gated on the new date's occurrence (the original date does not trigger release)

### Requirement: 収納代行 scheme — discharge on payment + 代理受領権限

The system's terms SHALL structure the money flow so the **buyer's payment
obligation is discharged on paying the platform** and the **Organizer grants the
platform 代理受領権限** (collection-agent authority), with the Organizer as the
**business seller-of-record**. This keeps the flow a collection agency (収納代行),
not 為替取引 / 資金移動業 / 前払式 (the load-bearing legal structure; see
payments-design counsel flag 1).

#### Scenario: Buyer obligation discharged at platform payment

- **WHEN** a buyer pays the platform for a ticket
- **THEN** their payment obligation to the Organizer is discharged at that moment (the platform holds as the Organizer's 代理受領 agent), and the Organizer is the seller-of-record

### Requirement: Refund taxonomy — cancellation vs postponement

On event **cancellation (中止)** the system SHALL refund the ticket's **current
holder** (which, for a ticket that changed hands via ⑦ official resale, is the
resale buyer — not necessarily the original purchaser) the **face value +
system/発券 fee** (retaining the payment-processor fee, JP norm) via a provider
refund and claw back the Organizer's share (`transfer_reversal`). If the ticket is
**listed/offered for resale** at cancellation time, the system SHALL **cancel that
listing/offer** and refund the holder (the resale fresh-sale leg MUST NOT run) —
this is the "normal cancellation-refund path" ⑦ defers to. On **postponement
(延期)** the system SHALL **not** auto-refund; the ticket stays valid for the new
date, **but SHALL offer a holder-initiated refund window** — a bounded period in
which a holder who cannot attend the rescheduled date may request a refund
(refunded like a cancellation: face + system/発券 fee, processor fee retained) —
the JP norm for postponed events.

#### Scenario: Postponement offers a holder-initiated refund window

- **WHEN** an event is postponed and a holder cannot attend the new date, within the refund window
- **THEN** the holder may request a refund (face + system/発券 fee, processor fee retained); outside the window the ticket simply stays valid for the new date

#### Scenario: Cancellation refunds the current holder

- **WHEN** an event is cancelled
- **THEN** the ticket's current holder is refunded face value + system/発券 fee (processor fee retained) and the Organizer's share is clawed back

#### Scenario: Cancellation supersedes a live resale listing

- **WHEN** an event is cancelled while a ticket is listed/offered for resale
- **THEN** the listing/offer is cancelled and the holder is refunded via this path (the resale fresh-sale leg does not run)

#### Scenario: Postponement keeps tickets valid

- **WHEN** an event is postponed
- **THEN** no automatic refund is issued and issued tickets remain valid for the new date

### Requirement: Consumer-price and return-policy disclosure (blocking)

The system SHALL render **all consumer-facing prices tax-inclusive (総額表示)** —
ticket and each fee as its own 税込 line plus a clear grand total — and SHALL show
a compliant **特商法 最終確認画面** before order confirmation that states 分量・
価格(税込)・**支払時期/方法** (incl. the **charge-only-if-you-win, at-the-draw,
via-saved-card** timing), 引渡時期, a **返品特約** ("no returns except event
cancellation/postponement" — omitting it triggers the 8-day statutory return
right), and per-Organizer **事業者情報**.

#### Scenario: Prices are tax-inclusive with a grand total

- **WHEN** any price is shown to a consumer
- **THEN** it is displayed tax-inclusive (each fee as a 税込 line) with a clear grand total

#### Scenario: Final confirmation screen states charge timing and 返品特約

- **WHEN** a buyer reaches the final confirmation screen
- **THEN** it states the charge-on-win timing/amount, 引渡時期, a 返品特約 (no returns except cancellation/postponement), and the Organizer's 事業者情報

<!-- Issuance also sets the buyer's ticket-journey to PAID. Because that changes
     the behavior of the EXISTING ticket-journey capability (adding a first-party
     issuance side-effect trigger), it is specified as a MODIFIED delta in
     specs/ticket-journey/spec.md, not as an ADDED requirement here. -->

### Requirement: No stored card data (PCI SAQ A)

The system SHALL collect card data only via the provider's hosted fields (Stripe
Elements) so **no PAN/CVC/expiry** touches our systems; it SHALL store only
provider tokens/customer references and maintain **PCI SAQ A** scope.

#### Scenario: Card data never reaches our systems

- **WHEN** a buyer enters card details
- **THEN** the details go directly to the provider and only opaque tokens are stored
