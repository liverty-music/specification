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
application and **captured at the draw** for winners — destination charge on behalf
of the Organizer with a platform application fee, JPY card only). ⑤ SHALL **NOT**
perform a separate off-session charge; on ④'s **captured winning payment**
(webhook-confirmed capture), ⑤ SHALL create the **Order** referencing that payment
and proceed to issuance. There is **no ⑤-side payment deadline, off-session charge,
re-auth, or 繰上げ** — the hold-and-capture model removes them (④ releases losers'
holds; a rare failed capture leaves the seat unfilled for manual follow-up, ④'s
concern).

#### Scenario: Order created from the captured winning payment

- **WHEN** ④ captures a winning application's held authorization (webhook-confirmed capture)
- **THEN** ⑤ creates an Order referencing that captured payment and proceeds to issuance

#### Scenario: ⑤ performs no separate charge

- **WHEN** a winner is being processed
- **THEN** ⑤ does not run an off-session charge / SetupIntent / payment-deadline / 繰上げ flow — the charge is ④'s capture of the held authorization

#### Scenario: Failed capture yields no Order

- **WHEN** ④'s capture of a winning authorization fails
- **THEN** ⑤ creates no Order and issues no ticket (the seat is left for ④'s manual follow-up; no ⑤-side retry/繰上げ)

### Requirement: Order record

The system SHALL create an **`Order`** for each purchase that is **provider- and
method-agnostic**: it stores opaque provider references (e.g. `pi_`/`pm_`), its
own `status` (`pending`/`paid`/`failed`/`refunded`), `amount`+`currency`,
`paid_at`, and optional display facets (card brand/last4) — **never** PAN, CVC,
or expiry. One Order SHALL cover the **N tickets** of the winning application.

#### Scenario: Order captures only opaque references

- **WHEN** an Order is created
- **THEN** it stores opaque provider token references and its own status/amount, and never stores PAN/CVC/expiry

#### Scenario: One Order spans the companion group

- **WHEN** a winning application for N tickets is charged
- **THEN** a single Order covers all N tickets

### Requirement: Issue account-bound tickets on confirmed capture

On a **webhook-confirmed** successful capture, the system SHALL issue **N
account-bound Tickets**. Each SHALL be a **covered ticket (特定興行入場券)** carrying
**all three** legal conditions: (i) the face states **resale without organizer
consent is prohibited**, (ii) the face specifies **date/venue + seat-or-eligible-
person**, and (iii) the **本人確認** (name + contact) is captured and noted on the
face, bound to the buyer's account. Tickets MUST NOT be issued on a client-side
confirmation alone.

#### Scenario: Tickets issued after webhook confirmation

- **WHEN** the provider webhook confirms the capture succeeded
- **THEN** N account-bound tickets are issued to the buyer

#### Scenario: Issued ticket carries all three covered-ticket conditions

- **WHEN** a ticket is issued
- **THEN** its face states resale-without-consent is prohibited, specifies date/venue + seat-or-eligible-person, and records the holder's 本人確認 (so it qualifies as a 特定興行入場券)

#### Scenario: No issuance on client confirm alone

- **WHEN** only the client reports success but no confirming webhook has arrived
- **THEN** no ticket is issued

### Requirement: Webhooks are the source of truth and idempotent

The system SHALL treat **provider webhooks** as the authoritative source for
capture / refund / dispute state, verify their signatures, and process them
**idempotently** (a redelivered or duplicated webhook MUST NOT double-issue,
double-refund, or double-charge).

#### Scenario: Duplicate webhook is idempotent

- **WHEN** the same capture webhook is delivered more than once
- **THEN** tickets are issued exactly once

<!-- The former "Charge outcome reporting (grace before void)" requirement is
     REMOVED: ④'s authorization-hold model (authorize at apply, capture on win,
     release on loss) has no off-session charge, no payment deadline, no
     re-auth/grace, and no 繰上げ — a held authorization captured at the draw
     effectively does not fail; a rare failed capture is ④'s manual-follow-up
     concern (see "Issue from ④'s captured winning payment"). -->

### Requirement: Payout held to event plus dispute buffer

Organizer payouts SHALL be on **manual payout**, released by a **scheduled
platform process** (not the Organizer) only after **the event's occurrence AND a
dispute-safety window**. "The event has occurred" SHALL be defined as **the
event's `start_time` (of its currently-scheduled date) having passed**; on a
**postponement (延期)** the release clock SHALL **reset to the new date** (never
release on a stale original date). The buyer's payment funds this held balance
under the 収納代行 scheme.

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
date.

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
