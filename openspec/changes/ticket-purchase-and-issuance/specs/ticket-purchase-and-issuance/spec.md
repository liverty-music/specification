## Purpose

This capability turns a lottery **win** into money and tickets: it charges the
winner's saved card off-session, records an Order, and issues Web2 account-bound
tickets — under the 収納代行 scheme with the Organizer as seller-of-record. It is
the primary payment + issuance pipeline for the ticketing MVP.

## ADDED Requirements

### Requirement: Charge a winner off-session

On a ④ **win**, the system SHALL charge the winner's **saved payment method**
(captured by ④'s SetupIntent) off-session via the provider, as a **destination
charge on behalf of the Organizer with a platform application fee**. It SHALL NOT
request CVC (so the charge remains a merchant-initiated transaction). The charge
SHALL be attempted within the winner's **payment deadline**. **Card-only** for
MVP (incl. debit/prepaid and wallet cards); other methods are out of scope.

#### Scenario: Winner is charged off-session

- **WHEN** an application wins and its payment deadline has not passed
- **THEN** the system charges the saved payment method off-session as a destination charge on behalf of the Organizer with the platform application fee, without requesting CVC

#### Scenario: Non-card method is not offered

- **WHEN** a purchase is initiated for MVP
- **THEN** only card (incl. debit/prepaid/wallet) is available; konbini/PayPay are not offered

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

### Requirement: Charge outcome reporting (grace before void)

The system SHALL report each off-session charge attempt's outcome to ④:
**succeeded**, **failed** (hard decline), or **needs re-authentication**
(`authentication_required` — a 3DS step-up, which occurs even for MIT under the JP
EMV-3DS regime). On **failed** or **needs-re-authentication** and while the
winner's payment deadline (owned by ④) **has not lapsed**, the system SHALL
surface a **re-auth / retry link** (a grace window) so the winner can complete the
step-up or fix their card — it MUST NOT immediately void the win. Only when ④
signals the deadline lapsed without success SHALL the Order be marked `failed` and
no ticket issued; ④ then runs 繰上げ. No ticket is issued for a non-succeeded
charge.

#### Scenario: Step-up gets a re-auth link within the deadline

- **WHEN** a charge returns needs-re-authentication (or a soft failure) before the deadline lapses
- **THEN** a re-auth/retry link is surfaced to the winner and the win is not voided yet

#### Scenario: Deadline lapse without success finalizes failure

- **WHEN** ④ signals the payment deadline lapsed with no successful charge
- **THEN** no ticket is issued, the Order is marked failed, and ④ runs 繰上げ

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
