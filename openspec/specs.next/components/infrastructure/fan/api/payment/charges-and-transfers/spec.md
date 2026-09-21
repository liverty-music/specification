# Charges And Transfers

## Purpose

This capability settles ticket money **out** to the Organizer. Buyer funds captured
by ④ sit on the **platform balance** (Stripe **separate charges & transfers**); after
the event this capability `Transfer`s the Organizer's net share (the platform retains
its fee) to the Organizer's **Stripe connected account**, and executes refunds/dispute
clawbacks — all under the 収納代行 scheme with the Organizer as seller-of-record.

## Requirements

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
