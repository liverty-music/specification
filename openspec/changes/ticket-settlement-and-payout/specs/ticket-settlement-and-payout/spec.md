## Purpose

This capability settles ticket money **out** to the Organizer. Buyer funds captured
by ④ sit on the **platform balance** (Stripe **separate charges & transfers**); after
the event this capability `Transfer`s the Organizer's net share (the platform retains
its fee) to the Organizer's **Stripe connected account**, and executes refunds/dispute
clawbacks — all under the 収納代行 scheme with the Organizer as seller-of-record.

## ADDED Requirements

### Requirement: Organizer Connect onboarding and payout eligibility

Each Organizer that receives payouts SHALL have a **Stripe connected account provisioned
as a payout recipient** (Accounts v2, requesting the **`transfers` capability** on
`stripe_balance`; the platform SHALL NOT request `card_payments` for it). A payout SHALL be
**blocked until that account's transfers capability is active** (identity verification /
KYC/KYB cleared). The platform SHALL be **responsible for connected-account negative
balances** (`losses_collector = application`), which is required for the
separate-charges-&-transfers model, for transfer reversals, and for any later
fund-isolation feature. An Organizer whose account is not payout-ready SHALL NOT block
ticket sale or issuance; only the **payout** waits.

#### Scenario: Payout blocked until KYC clears

- **WHEN** a payout is due to an Organizer whose connected account has not completed identity verification
- **THEN** the payout is withheld (not failed) until verification completes, and sales/issuance are unaffected

#### Scenario: Verified Organizer is payout-eligible

- **WHEN** an Organizer's connected account has its transfers capability active (KYC/KYB cleared)
- **THEN** the Organizer is eligible to receive the scheduled post-event Transfer

### Requirement: Hold-to-event payout via separate charges and transfers

Buyer funds SHALL be **held on the platform balance** (a plain platform charge captured
by ④ — **not** a destination charge, which would settle to the Organizer at capture).
After the release gate, a **scheduled platform process** (not the Organizer) SHALL
create a Stripe **`Transfer` with `source_transaction` = the captured charge** to the
Organizer's connected account for the Organizer's **net share**, and the platform SHALL
**retain its fee as the un-transferred remainder** (no self-transfer). The system SHALL
NOT use `allocated_funds` (funds segregation) while it is unavailable for Japan; funds
remain in the general platform balance until the Transfer.

#### Scenario: Post-event Transfer settles the Organizer's net share

- **WHEN** the release gate has passed for a captured winning order
- **THEN** the platform transfers the Organizer's net share to their connected account (source_transaction = the charge) and retains the platform fee as the remainder

#### Scenario: Funds are held on the platform balance until release

- **WHEN** a charge is captured but the release gate has not passed
- **THEN** the funds remain on the platform balance (no Transfer yet), held under the 収納代行 scheme

### Requirement: Settlement splits — single Organizer payee, extensible

Payout SHALL be modelled as a set of **settlement splits** (payee reference + amount or
share). The **MVP SHALL define exactly one split — the Organizer** — plus the retained
platform fee; the **venue is the Organizer's own cost, not a platform payee**. The model
SHALL admit **additional payees** (e.g. venue, artist) later without a schema-breaking
change; adding one is connected-account onboarding + a split entry, each realized as its
own `Transfer` with `source_transaction` = the same charge (sum of splits ≤ charge).

#### Scenario: MVP settles a single Organizer split

- **WHEN** an order is settled in the MVP
- **THEN** there is exactly one payout split (the Organizer) and the platform fee is the retained remainder

#### Scenario: Additional payee added without a breaking change

- **WHEN** a venue or artist payee is introduced later
- **THEN** it is represented as an additional settlement split (its own Transfer against the same charge), with the total of all splits not exceeding the charge amount

### Requirement: Payout release gated on event occurrence plus dispute buffer

A payout Transfer SHALL be released only after **the event's `start_time` (of its
currently-scheduled date) has passed AND a dispute-safety window has elapsed**. On a
**postponement (延期)** the release clock SHALL **reset to the new date** (never release
on a stale original date). This counter-performance gate is load-bearing for the 収納代行
characterization (the gate matters, not a bright-line N-day).

#### Scenario: No release before event plus buffer

- **WHEN** the event's current start_time has not passed, or the dispute buffer has not elapsed
- **THEN** the Organizer payout for that sale is not released

#### Scenario: Postponement resets the release clock

- **WHEN** an event is postponed to a later date
- **THEN** the payout release is re-gated on the new date (the original date does not trigger release)

### Requirement: Contractual seller-of-record with a recognizable statement descriptor

The Organizer SHALL be the **single seller-of-record contractually** (代理受領権限 grant +
特商法 表記 naming the Organizer as 販売業者), while the **platform is the Stripe settlement
merchant** and the 収納代行 collection agent holding the funds. The charge SHALL NOT use
`on_behalf_of` (which would require the Organizer's connected account to hold the
`card_payments` capability active before the charge, gating ticket sale on merchant KYB).
The buyer's card statement SHALL show a **recognizable descriptor** — the platform's static
prefix plus a **per-event dynamic suffix** (Latin, and JP kanji/kana for JP-issued cards)
identifying the event/organizer — to reduce "unrecognized charge" disputes.

#### Scenario: Platform is the settlement merchant; Organizer is contractual seller

- **WHEN** a charge is created for a ticket
- **THEN** the charge does not set on_behalf_of (the platform is the Stripe settlement merchant), while the Organizer remains the contractual seller-of-record and the platform holds the funds as collection agent

#### Scenario: Statement descriptor identifies the event

- **WHEN** the charge appears on the buyer's card statement
- **THEN** it shows the platform prefix plus a per-event suffix identifying the event/organizer

### Requirement: Refund and dispute clawback across splits

The refund **entry point** is ⑤'s `OrderAdminService.RefundOrder` (already defined in
#938); this capability provides the **money movement** it invokes. Refunds and disputes
SHALL be executed from the **platform balance** (`Refund` for the buyer), and any
Organizer share already transferred SHALL be **clawed back per split via
`transfer_reversal`**. The system SHALL hold a **reserve past the dispute window** so a
chargeback arriving after payout does not strand the platform, and it SHALL process
inbound refund/dispute provider webhooks **idempotently** (no double-refund, no
double-reversal). ⑤ owns the refund **policy + RPC** (cancellation refunds the current
holder; postponement offers a bounded holder-initiated window); this capability moves
the money.

#### Scenario: Refund reverses each transferred split

- **WHEN** a refund is owed for an order whose shares were already transferred
- **THEN** the buyer is refunded from the platform balance and each transferred split is reversed via transfer_reversal

#### Scenario: Chargeback after payout draws on the reserve

- **WHEN** a chargeback arrives after the Organizer payout was released
- **THEN** the platform absorbs it against the held reserve / negative-balance responsibility and reverses the Organizer's transfer

#### Scenario: Refund webhook is idempotent

- **WHEN** a refund/dispute webhook is delivered more than once
- **THEN** the refund and reversals are applied exactly once
