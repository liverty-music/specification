# components/adapter/fan/api/rpc/lottery-entry Specification

## Purpose
The fan-facing lottery entry service boundary (`LotteryEntryService`): how a signed-in fan's call becomes a LotteryEntryUseCase call for that fan's own entries.

## Requirements

### Requirement: The fan entering is the signed-in caller

Every lottery entry call (Start, AuthorizeCard, Confirm, Withdraw and ListByTicketType) SHALL require a signed-in caller and fail with Unauthenticated otherwise. It SHALL resolve the caller to their stored User (User.GetByProviderUserID), failing with NotFound when the caller has no stored account, and pass that User to LotteryEntryUseCase.Start, AuthorizeCard, Confirm, Withdraw or ListByTicketType; the request never names a user. AuthorizeCard SHALL return the card authorization secret (`card_authorization_secret`) the usecase returns. Errors from the usecase SHALL be returned unchanged.

#### Scenario: Fan starts an entry
- **WHEN** a signed-in fan calls Start for a TicketType
- **THEN** the Draft is made with that fan as its user

#### Scenario: Not signed in
- **WHEN** a caller who is not signed in calls ListByTicketType
- **THEN** the call fails with Unauthenticated and no usecase runs

#### Scenario: Caller without an account
- **WHEN** a signed-in caller with no stored account calls Start
- **THEN** the call fails with NotFound and nothing is stored

#### Scenario: Withdraw own entry
- **WHEN** a fan calls Withdraw with the id of their own Entered entry
- **THEN** LotteryEntryUseCase.Withdraw runs with that fan and the entry is withdrawn

### Requirement: Lottery entry requests are validated at the boundary

Each call SHALL fail with InvalidArgument, before any usecase runs, when:
- Start or ListByTicketType names no TicketType;
- Start's ticket count is not greater than 0;
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
