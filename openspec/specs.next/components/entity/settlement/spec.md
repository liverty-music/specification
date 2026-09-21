# Settlement

## Purpose

This capability settles ticket money **out** to the Organizer. Buyer funds captured
by ④ sit on the **platform balance** (Stripe **separate charges & transfers**); after
the event this capability `Transfer`s the Organizer's net share (the platform retains
its fee) to the Organizer's **Stripe connected account**, and executes refunds/dispute
clawbacks — all under the 収納代行 scheme with the Organizer as seller-of-record.

## Requirements

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
