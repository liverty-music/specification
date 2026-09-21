# Refund Order

## Purpose

Refunds a buyer's captured ticket payment when issuance fails or an event is cancelled or postponed, and claws back funds already split out to the organizer when a refund or dispute occurs.

## Requirements

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
