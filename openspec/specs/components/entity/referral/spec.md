# components/entity/referral Specification

## Purpose
A ReferralCode is the code a link to an event carries, so that the Organizer can count the purchases each link brought. A Checkout or a LotteryEntry keeps the code the fan came with as its referral code. The code is free-form: it is not registered in advance, grants no access and pays no reward.

The value ReferralCode is 1 to 32 characters, each a lowercase ASCII letter (a–z), a digit (0–9) or a hyphen.

## Requirements

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
