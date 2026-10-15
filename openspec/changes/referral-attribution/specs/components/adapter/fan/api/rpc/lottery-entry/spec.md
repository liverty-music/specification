## MODIFIED Requirements

### Requirement: Lottery entry requests are validated at the boundary

Each call SHALL fail with InvalidArgument, before any usecase runs, when:
- Start or ListByTicketType names no TicketType;
- Start's ticket count is not greater than 0;
- Start's referral code is given and is not a valid ReferralCode (1 to 32 lowercase ASCII letters, digits or hyphens); a Start without a referral code is valid;
- AuthorizeCard, Confirm or Withdraw names no LotteryEntry;
- AuthorizeCard's full name or phone number is missing or breaks the User's personal details rule, including a phone number that is not in E.164 form.

#### Scenario: Zero tickets
- **WHEN** Start is called with a ticket count of 0
- **THEN** it fails with InvalidArgument and nothing is stored

#### Scenario: Domestic-format phone number
- **WHEN** AuthorizeCard is called with the phone number `090-1234-5678`
- **THEN** it fails with InvalidArgument and no card authorization is opened

#### Scenario: E.164 phone number
- **WHEN** AuthorizeCard is called with the phone number `+819012345678` and every other field valid
- **THEN** the request passes the boundary and LotteryEntryUseCase.AuthorizeCard runs

#### Scenario: Malformed referral code
- **WHEN** Start is called with a referral code of 33 characters
- **THEN** it fails with InvalidArgument, nothing is stored and no Referral is recorded

#### Scenario: Referral code passed on
- **WHEN** Start is called with a TicketType, a ticket count of 2 and the referral code `member-a`
- **THEN** the request passes the boundary and LotteryEntryUseCase.Start runs with the code `member-a`
