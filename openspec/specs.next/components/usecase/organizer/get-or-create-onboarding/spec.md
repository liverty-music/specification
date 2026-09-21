# Get Or Create Onboarding

## Purpose

This capability settles ticket money **out** to the Organizer. Buyer funds captured
by ④ sit on the **platform balance** (Stripe **separate charges & transfers**); after
the event this capability `Transfer`s the Organizer's net share (the platform retains
its fee) to the Organizer's **Stripe connected account**, and executes refunds/dispute
clawbacks — all under the 収納代行 scheme with the Organizer as seller-of-record.

## Requirements

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
