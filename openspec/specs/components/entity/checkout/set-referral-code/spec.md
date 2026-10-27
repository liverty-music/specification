# components/entity/checkout/set-referral-code Specification

## Purpose
Checkout.SetReferralCode sets the referral code of a fan's Held Checkout, replacing an earlier one, so the last link the fan followed before paying is the one that counts.

## Requirements

### Requirement: The code of a Held checkout is set

SetReferralCode SHALL take a Checkout and a ReferralCode. When the Checkout is Held it SHALL set its referral code, replacing any earlier code. When the Checkout is not Held it SHALL change nothing and succeed, so a start that races a commit never alters a committed Checkout. Checking the status and setting the code SHALL be one indivisible step. It SHALL fail with FailedPrecondition when the Checkout does not exist.

#### Scenario: First code
- **WHEN** SetReferralCode is called with `member-a` for a Held Checkout without a code
- **THEN** its referral code is `member-a`

#### Scenario: Last link wins
- **WHEN** a Held Checkout has the code `member-a` and SetReferralCode is called with `member-b`
- **THEN** its referral code is `member-b`

#### Scenario: Committed checkout keeps its code
- **WHEN** a Committed Checkout has the code `member-a` and SetReferralCode is called with `member-b`
- **THEN** its referral code stays `member-a` and SetReferralCode succeeds

#### Scenario: Unknown checkout
- **WHEN** no Checkout has the given id
- **THEN** SetReferralCode fails with FailedPrecondition
