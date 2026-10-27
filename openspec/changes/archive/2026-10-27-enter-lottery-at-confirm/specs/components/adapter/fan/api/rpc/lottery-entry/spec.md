## MODIFIED Requirements


### Requirement: Lottery entry requests are validated at the boundary

Each call SHALL fail with InvalidArgument, before any usecase runs, when:
- AuthorizeCard or ListByTicketType names no TicketType;
- AuthorizeCard's ticket count is not greater than 0;
- AuthorizeCard's referral code is given and is not a valid ReferralCode (1 to 32 lowercase ASCII letters, digits or hyphens); an AuthorizeCard without a referral code is valid;
- AuthorizeCard's full name or phone number is missing or breaks the User's personal details rule, including a phone number that is not in E.164 form;
- Confirm names no card authorization.

#### Scenario: Zero tickets
- **WHEN** AuthorizeCard is called with a ticket count of 0
- **THEN** it fails with InvalidArgument and no card authorization is opened

#### Scenario: Domestic-format phone number
- **WHEN** AuthorizeCard is called with the phone number `090-1234-5678`
- **THEN** it fails with InvalidArgument and no card authorization is opened

#### Scenario: E.164 phone number
- **WHEN** AuthorizeCard is called with the phone number `+819012345678` and every other field valid
- **THEN** the request passes the boundary and LotteryEntryUseCase.AuthorizeCard runs

#### Scenario: Malformed referral code
- **WHEN** AuthorizeCard is called with a referral code of 33 characters
- **THEN** it fails with InvalidArgument and no card authorization is opened

#### Scenario: Referral code passed on
- **WHEN** AuthorizeCard is called with a TicketType, a ticket count of 2, valid details and the referral code `member-a`
- **THEN** the request passes the boundary and LotteryEntryUseCase.AuthorizeCard runs with the code `member-a`

## ADDED Requirements

### Requirement: Every lottery entry call is made by the signed-in fan

Every lottery entry call (AuthorizeCard, Confirm and ListByTicketType) SHALL require a signed-in caller and fail with Unauthenticated otherwise. It SHALL resolve the caller to their stored User (User.GetByProviderUserID), failing with NotFound when the caller has no stored account, and pass that User to LotteryEntryUseCase.AuthorizeCard, Confirm or ListByTicketType; the request never names a user. AuthorizeCard SHALL return the card authorization's id (`card_authorization_id`) and its secret (`card_authorization_secret`) the usecase returns, and Confirm the entry it makes. Errors from the usecase SHALL be returned unchanged.

#### Scenario: Fan authorizes their card
- **WHEN** a signed-in fan calls AuthorizeCard for a TicketType
- **THEN** the card authorization is opened for that fan

#### Scenario: Not signed in
- **WHEN** a caller who is not signed in calls ListByTicketType
- **THEN** the call fails with Unauthenticated and no usecase runs

#### Scenario: Caller without an account
- **WHEN** a signed-in caller with no stored account calls AuthorizeCard
- **THEN** the call fails with NotFound and no card authorization is opened

#### Scenario: Fan confirms
- **WHEN** a fan calls Confirm with the id of their own Authorized card authorization
- **THEN** LotteryEntryUseCase.Confirm runs with that fan and the Entered entry is returned

## REMOVED Requirements

### Requirement: The fan entering is the signed-in caller
**Reason**: Start and Withdraw are removed, and AuthorizeCard returns the card authorization id.
**Migration**: Replaced by "Every lottery entry call is made by the signed-in fan".
