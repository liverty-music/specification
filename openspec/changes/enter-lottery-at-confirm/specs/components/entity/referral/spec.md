## MODIFIED Requirements

### Requirement: Referral code format

A ReferralCode SHALL be 1 to 32 characters long and consist only of lowercase ASCII letters, digits and hyphens. Uppercase letters are not part of a ReferralCode: the fan app lowercases a link's code before it keeps it, so `Member-A` and `member-a` in links are the same code.

#### Scenario: Code from a link
- **WHEN** the code is `member-a`
- **THEN** it is a valid ReferralCode

#### Scenario: Empty or too long
- **WHEN** the code is empty or 33 characters long
- **THEN** it is not a valid ReferralCode

#### Scenario: Other characters
- **WHEN** the code is `member_a`, `メンバーA`, `a b` or `Member-A`
- **THEN** it is not a valid ReferralCode

#### Scenario: One code whatever the case in links
- **WHEN** one fan arrives through `?ref=Member-A` and another through `?ref=member-a`, and both buy
- **THEN** both purchases have the referral code `member-a`

## REMOVED Requirements

### Requirement: Exactly one source
**Reason**: The Referral entity is folded into the referral code of a Checkout and of a LotteryEntry; a code has no source of its own.
**Migration**: The schema migration copies each Referral's code onto its Checkout or LotteryEntry and drops the referrals.

### Requirement: The code changes only before the source is confirmed
**Reason**: Moved to the purchase: a Checkout's code changes only while Held (Checkout.SetReferralCode); a LotteryEntry's code is set when it is created.
**Migration**: None.

### Requirement: A Referral lives with its source
**Reason**: The code is an attribute of its Checkout or LotteryEntry, so it is removed or kept with it.
**Migration**: None.
