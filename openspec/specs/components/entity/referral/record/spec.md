# components/entity/referral/record Specification

## Purpose
Referral.Record stores the referral code a Checkout or a LotteryEntry was started with, replacing an earlier code while the source is still open, so the last link a fan followed before confirming is the one that counts.

## Requirements

### Requirement: Record keeps the last code of an open source

Record SHALL take a source (a Checkout or a LotteryEntry), a ReferralCode and a time:
- When the source has no Referral and is open, it SHALL create a Referral with the code and the time as its create time.
- When the source has a Referral with the same code, it SHALL change nothing.
- When the source has a Referral with another code and is open, it SHALL replace the code and keep the create time.
- When the source is not open, it SHALL change nothing and succeed, so a start that races a confirmation never alters a confirmed source.

Checking the source and writing SHALL be one indivisible step, so two concurrent calls for the same source leave exactly one Referral, holding one of the two codes. Record SHALL fail with FailedPrecondition and store nothing when the source does not exist. It returns nothing.

#### Scenario: First code
- **WHEN** Record is called with `member-a` for a Held Checkout that has no Referral
- **THEN** the Checkout has a Referral with the code `member-a`

#### Scenario: Same code again
- **WHEN** a Held Checkout's Referral has the code `member-a` and Record is called with `member-a`
- **THEN** nothing changes

#### Scenario: Last link wins
- **WHEN** a Draft LotteryEntry's Referral has the code `member-a` and Record is called with `member-b`
- **THEN** the Referral's code is `member-b` and its create time is unchanged

#### Scenario: Confirmed source keeps its code
- **WHEN** an Entered LotteryEntry's Referral has the code `member-a` and Record is called with `member-b`
- **THEN** the Referral's code stays `member-a` and Record succeeds

#### Scenario: Confirmed source without a code
- **WHEN** Record is called with `member-a` for a Committed Checkout that has no Referral
- **THEN** no Referral is created and Record succeeds

#### Scenario: Concurrent records
- **WHEN** Record is called for the same Held Checkout with `member-a` and `member-b` at the same time
- **THEN** the Checkout has exactly one Referral, with one of the two codes

#### Scenario: Unknown source
- **WHEN** no Checkout has the given id
- **THEN** Record fails with FailedPrecondition and stores nothing
