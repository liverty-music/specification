## ADDED Requirements

### Requirement: Every lottery entry call is made by the signed-in fan

Every lottery entry call (Start, AuthorizeCard, Confirm and ListByTicketType) SHALL require a signed-in caller and fail with Unauthenticated otherwise. It SHALL resolve the caller to their stored User (User.GetByProviderUserID), failing with NotFound when the caller has no stored account, and pass that User to LotteryEntryUseCase.Start, AuthorizeCard, Confirm or ListByTicketType; the request never names a user. AuthorizeCard SHALL return the card authorization secret (`card_authorization_secret`) the usecase returns. Errors from the usecase SHALL be returned unchanged.

#### Scenario: Fan starts an entry
- **WHEN** a signed-in fan calls Start for a TicketType
- **THEN** the Draft is made with that fan as its user

#### Scenario: Not signed in
- **WHEN** a caller who is not signed in calls ListByTicketType
- **THEN** the call fails with Unauthenticated and no usecase runs

#### Scenario: Caller without an account
- **WHEN** a signed-in caller with no stored account calls Start
- **THEN** the call fails with NotFound and nothing is stored

## MODIFIED Requirements

### Requirement: Lottery entry requests are validated at the boundary

Each call SHALL fail with InvalidArgument, before any usecase runs, when:
- Start or ListByTicketType names no TicketType;
- Start's ticket count is not greater than 0;
- Start's referral code is given and is not a valid ReferralCode (1 to 32 lowercase ASCII letters, digits or hyphens); a Start without a referral code is valid;
- AuthorizeCard or Confirm names no LotteryEntry;
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

## REMOVED Requirements

### Requirement: The fan entering is the signed-in caller
**Reason**: The Withdraw call is removed.
**Migration**: Replaced by "Every lottery entry call is made by the signed-in fan" for the four remaining calls.
