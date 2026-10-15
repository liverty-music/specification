## ADDED Requirements

### Requirement: Record the referral code the entry started with

Start SHALL also take an optional ReferralCode. When a code is given and LotteryEntry.GetOrCreateDraft returns a Draft, Start SHALL call Referral.Record for that Draft with the code and the current time before it returns the Draft, and SHALL return a failure of Referral.Record unchanged; starting again resumes the same Draft and records the code again. When no code is given, Start SHALL record nothing and an existing Referral of the Draft stays as it is. When an earlier check fails, nothing is recorded. Start SHALL NOT check the code against any list or against the event's Series; any valid ReferralCode is recorded.

#### Scenario: Entry from a referral link
- **WHEN** a fan starts an entry for 2 tickets of an open sale's TicketType with the code `member-a`
- **THEN** the Draft is returned and its Referral has the code `member-a`

#### Scenario: Another link before confirming
- **WHEN** the fan's Draft has the code `member-a` and the fan starts again with the same count and the code `member-b`
- **THEN** the same Draft is returned and its Referral's code is `member-b`

#### Scenario: Started again without a code
- **WHEN** the fan's Draft has the code `member-a` and the fan starts again with the same count and no code
- **THEN** the same Draft is returned and its Referral keeps `member-a`

#### Scenario: Already entered with a code
- **WHEN** the fan already has an Entered entry for the TicketType whose Referral has the code `member-a`, and starts again with the code `member-b`
- **THEN** Start fails with FailedPrecondition and the Referral keeps `member-a`
