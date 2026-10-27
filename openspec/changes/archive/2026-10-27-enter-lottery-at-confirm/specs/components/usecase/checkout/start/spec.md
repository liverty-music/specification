## MODIFIED Requirements

### Requirement: Record the referral code the checkout started with

Start SHALL also take an optional ReferralCode. When a code is given and Checkout.GetOrCreateHeld returns a Checkout, Start SHALL set the code on that Checkout with Checkout.SetReferralCode before it returns the Checkout, and SHALL return a failure of Checkout.SetReferralCode unchanged; the hold stays, so starting again resumes the same Checkout and sets the code again. When no code is given, Start SHALL set nothing and an existing code of the Checkout stays as it is. When an earlier check fails, nothing is set. Start SHALL NOT check the code against any list or against the event's Series; any valid ReferralCode is set.

#### Scenario: Checkout from a referral link
- **WHEN** a fan starts a checkout for 2 tickets of an OnSale TicketType with the code `member-a`
- **THEN** the Checkout is returned with the referral code `member-a`

#### Scenario: Another link before confirming
- **WHEN** the fan's Held Checkout has the code `member-a` and the fan starts again with the same count and the code `member-b`
- **THEN** the same Checkout is returned with the referral code `member-b`

#### Scenario: Started again without a code
- **WHEN** the fan's Held Checkout has the code `member-a` and the fan starts again with the same count and no code
- **THEN** the same Checkout is returned and keeps `member-a`

#### Scenario: No code
- **WHEN** a fan starts a checkout without a code
- **THEN** the Checkout has no referral code

#### Scenario: Sale not open with a code
- **WHEN** a fan starts a checkout with the code `member-a` for a NotYetOnSale TicketType
- **THEN** Start fails with FailedPrecondition and no code is set
