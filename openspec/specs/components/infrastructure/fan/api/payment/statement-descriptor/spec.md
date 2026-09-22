# Statement Descriptor

## Purpose

This capability settles ticket money **out** to the Organizer. Buyer funds captured
by ④ sit on the **platform balance** (Stripe **separate charges & transfers**); after
the event this capability `Transfer`s the Organizer's net share (the platform retains
its fee) to the Organizer's **Stripe connected account**, and executes refunds/dispute
clawbacks — all under the 収納代行 scheme with the Organizer as seller-of-record.

## Requirements

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
