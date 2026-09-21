<!-- merge_group: REFUND | target: components/usecase/order/refund-order | members: 1 -->

<!-- member: ticket-purchase-and-issuance | flags:  -->
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

