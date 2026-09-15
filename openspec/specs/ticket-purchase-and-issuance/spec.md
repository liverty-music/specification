# ticket-purchase-and-issuance Specification

## Purpose
This capability turns a **captured** lottery win into an Order and issued tickets:
④ **authorizes (holds) the card at application and captures the winner's
authorization at the draw**; ⑤ takes that **captured winning payment** and records
an Order + issues Web2 account-bound tickets — under the 収納代行 scheme with the
Organizer as seller-of-record. It is the primary Order + issuance pipeline for the
ticketing MVP.
## Requirements
### Requirement: Issue from ④'s captured winning payment

The charge is performed by **④** (a Stripe **manual-capture** authorization held at
application and **captured at the draw** for winners, JPY card only). The captured
funds land on the **platform balance** (④'s charge is a plain platform charge, so it
already holds funds under the 収納代行 scheme); the post-event settlement of the
Organizer's net share is owned by **`ticket-settlement-and-payout`** (see the
delegation requirement below). **④ owns the PaymentIntent lifecycle and its provider
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

### Requirement: Idempotent issuance

**Capture** and its provider webhooks belong to ④; **refund/dispute** provider
webhooks and their idempotency belong to **`ticket-settlement-and-payout`** (which
makes the refund calls). ⑤ SHALL make **issuance idempotent**: replaying the
Won-captured signal (or retrying issuance) MUST NOT double-issue tickets or
double-create an Order for the same application.

#### Scenario: Replayed captured-win signal issues exactly once

- **WHEN** ④'s Won-captured signal for an application is observed/retried more than once
- **THEN** the Order is created once and tickets are issued exactly once

### Requirement: Capture succeeded but issuance failed

If ④'s capture **succeeded** but ⑤ **cannot complete issuance** (e.g. a persistence
error after capture), ⑤ MUST NOT leave money captured with no ticket. ⑤ SHALL
**retry issuance idempotently**; if issuance still cannot complete within a bounded
window it SHALL **refund/void the captured payment** (the refund executed via
`ticket-settlement-and-payout`: `Refund` + `transfer_reversal`) and surface the case
for operator follow-up. It MUST never double-issue on a later retry.

#### Scenario: Post-capture issuance failure is reconciled

- **WHEN** the capture succeeded but ticket issuance fails
- **THEN** ⑤ retries issuance idempotently, and if it still cannot complete it refunds the captured payment and flags the case (money is never captured with no ticket, and no double issuance occurs)

<!-- The former "Charge outcome reporting (grace before void)" requirement is
     REMOVED: ④'s authorization-hold model (authorize at apply, capture on win,
     release on loss) has no off-session charge, no payment deadline, no
     re-auth/grace, and no 繰上げ — a held authorization captured at the draw
     effectively does not fail; a rare failed capture is ④'s manual-follow-up
     concern (see "Issue from ④'s captured winning payment"). -->

### Requirement: Settlement and payout are delegated to ticket-settlement-and-payout

⑤ issues the Order + Tickets from ④'s captured payment and owns the refund
**policy** (cancellation/postponement taxonomy, below). The **money-out layer** —
holding funds on the platform balance until the event, the post-event `Transfer` of
the Organizer's net share (platform fee retained) via separate charges & transfers,
Organizer Stripe Connect onboarding, the hold-to-event + dispute-buffer release gate,
and refund/dispute `transfer_reversal` **execution** — is owned by the
**`ticket-settlement-and-payout`** capability. ⑤ SHALL NOT itself perform the payout
Transfer; it records the Order that settlement settles against.

#### Scenario: ⑤ does not perform the payout

- **WHEN** an Order is created and its tickets issued
- **THEN** the post-event Organizer payout (and any refund clawback) is performed by ticket-settlement-and-payout, not by ⑤

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
refund and claw back the Organizer's share (`transfer_reversal`) — this refund/
clawback is **executed by `ticket-settlement-and-payout`**; ⑤ owns the policy (who
is refunded, what amount). If the ticket is
**listed/offered for resale** at cancellation time, the system SHALL **cancel that
listing/offer** and refund the holder (the resale fresh-sale leg MUST NOT run) —
this is the "normal cancellation-refund path" ⑦ defers to. On **postponement
(延期)** the system SHALL **not** auto-refund; the ticket stays valid for the new
date, **but SHALL offer a holder-initiated refund window** — a bounded period in
which a holder who cannot attend the rescheduled date may request a refund
(refunded like a cancellation: face + system/発券 fee, processor fee retained) —
the JP norm for postponed events. The window SHALL be measured from a
**server-owned reschedule/announcement timestamp** (`Event.rescheduled_time`),
stamped by the platform when the organizer reschedules — independent of the
refund caller — so the window cannot be measured from the purchase/capture time
(which would reject every advance-purchase refund) nor set by the same admin
caller it constrains.

#### Scenario: Postponement offers a holder-initiated refund window

- **WHEN** an event is postponed and a holder cannot attend the new date, within the window measured from `Event.rescheduled_time`
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

<!-- The consumer-price (総額表示) and 特商法 最終確認画面 disclosure requirement
     moved to the `payments-legal-compliance` capability (its "Total-price display"
     and "特定商取引法 final confirmation" requirements). It is a livemode launch
     gate spanning ④/⑤ checkout surfaces, not an ⑤ issuance behavior. -->

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

