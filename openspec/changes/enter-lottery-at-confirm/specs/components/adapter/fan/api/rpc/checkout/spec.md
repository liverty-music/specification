## MODIFIED Requirements

### Requirement: Requests are validated before any usecase runs

Before any usecase runs, the boundary SHALL fail with InvalidArgument when:
- Start's TicketType is missing or malformed, or its ticket count is missing or not greater than 0;
- Start's referral code is given and is not a valid ReferralCode (1 to 32 lowercase ASCII letters, digits or hyphens); a Start without a referral code is valid;
- the Checkout of Get, AuthorizeCard or Confirm is missing or malformed;
- AuthorizeCard's full name or phone number is missing or breaks the User's personal details rule, including a phone number that is not in E.164 form.

#### Scenario: Missing name
- **WHEN** AuthorizeCard is called without a full name
- **THEN** it fails with InvalidArgument and no card authorization is opened

#### Scenario: Zero tickets
- **WHEN** Start is called with a ticket count of 0
- **THEN** it fails with InvalidArgument and nothing is held

#### Scenario: Domestic-format phone number
- **WHEN** AuthorizeCard is called with the phone number `090-1234-5678`
- **THEN** it fails with InvalidArgument and no card authorization is opened

#### Scenario: Malformed referral code
- **WHEN** Start is called with the referral code `member_a`
- **THEN** it fails with InvalidArgument, nothing is held and no referral code is set

#### Scenario: Referral code passed on
- **WHEN** Start is called with a valid TicketType, a ticket count of 2 and the referral code `member-a`
- **THEN** the request passes the boundary and CheckoutUseCase.Start runs with the code `member-a`
