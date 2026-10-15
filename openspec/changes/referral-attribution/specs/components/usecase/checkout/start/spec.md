## ADDED Requirements

### Requirement: Record the referral code the checkout started with

Start SHALL also take an optional ReferralCode. When a code is given and Checkout.GetOrCreateHeld returns a Checkout, Start SHALL call Referral.Record for that Checkout with the code and the current time before it returns the Checkout, and SHALL return a failure of Referral.Record unchanged; the hold stays, so starting again resumes the same Checkout and records the code again. When no code is given, Start SHALL record nothing and an existing Referral of the Checkout stays as it is. When an earlier check fails, nothing is recorded. Start SHALL NOT check the code against any list or against the event's Series; any valid ReferralCode is recorded.

#### Scenario: Checkout from a referral link
- **WHEN** a fan starts a checkout for 2 tickets of an OnSale TicketType with the code `member-a`
- **THEN** the Checkout is returned and its Referral has the code `member-a`

#### Scenario: Another link before confirming
- **WHEN** the fan's Held Checkout has the code `member-a` and the fan starts again with the same count and the code `member-b`
- **THEN** the same Checkout is returned and its Referral's code is `member-b`

#### Scenario: Started again without a code
- **WHEN** the fan's Held Checkout has the code `member-a` and the fan starts again with the same count and no code
- **THEN** the same Checkout is returned and its Referral keeps `member-a`

#### Scenario: No code
- **WHEN** a fan starts a checkout without a code
- **THEN** the Checkout has no Referral

#### Scenario: Sale not open with a code
- **WHEN** a fan starts a checkout with the code `member-a` for a NotYetOnSale TicketType
- **THEN** Start fails with FailedPrecondition and no Referral is recorded
