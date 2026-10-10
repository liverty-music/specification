# Spec Delta

## ADDED Requirements

### Requirement: The fan entering is the signed-in caller

Every lottery entry call SHALL require a signed-in caller and fail with Unauthenticated otherwise. Create, Withdraw, Get and GetResult SHALL resolve the caller to their stored User (User.GetByExternalID) and pass that User to LotteryUseCase.Enter, WithdrawEntry, GetMyEntry and GetResult; the request never names a user. When the caller has no stored account, these calls SHALL fail with NotFound. CreateAuthorization only opens a card hold for a TicketType and ticket count, so it requires the sign-in but looks up no account and passes no user.

#### Scenario: Fan enters
- **WHEN** a signed-in fan calls Create for a TicketType
- **THEN** the entry is made with that fan as its user

#### Scenario: Not signed in
- **WHEN** a caller who is not signed in calls GetResult
- **THEN** the call fails with Unauthenticated and no usecase runs

#### Scenario: Caller without an account
- **WHEN** a signed-in caller with no stored account calls Create
- **THEN** the call fails with NotFound and nothing is entered

### Requirement: Withdrawal names the ticket type, not the entry

Withdraw SHALL take a TicketType; the boundary SHALL find the caller's own entry for that TicketType with LotteryUseCase.GetMyEntry and withdraw it with LotteryUseCase.WithdrawEntry. When the caller has no entry for the TicketType, the call SHALL fail with NotFound and nothing is withdrawn.

#### Scenario: Withdraw own entry
- **WHEN** a fan with an entry for the TicketType calls Withdraw for it
- **THEN** that entry is withdrawn

#### Scenario: No entry
- **WHEN** a fan with no entry for the TicketType calls Withdraw
- **THEN** it fails with NotFound

### Requirement: Lottery entry requests are validated at the boundary

Every lottery entry call SHALL fail with InvalidArgument, before any usecase runs, when no TicketType is given. CreateAuthorization and Create SHALL fail with InvalidArgument when the requested ticket count is not greater than 0; Create SHALL also fail with InvalidArgument when the full name, the phone number or the card authorization is missing, or when the full name or phone number breaks the User's personal details rule, including a phone number that is not in E.164 form.

#### Scenario: Zero tickets
- **WHEN** Create is called with a requested ticket count of 0
- **THEN** it fails with InvalidArgument and nothing is entered

#### Scenario: Domestic-format phone number
- **WHEN** Create is called with the phone number `090-1234-5678`
- **THEN** it fails with InvalidArgument and nothing is entered

#### Scenario: E.164 phone number
- **WHEN** Create is called with the phone number `+819012345678` and every other field valid
- **THEN** the request passes the boundary and LotteryUseCase.Enter runs

## REMOVED Requirements

### Requirement: The applicant is the signed-in caller
**Reason**: The applicant is now the LotteryEntry's user, and the calls take a TicketType instead of a LotterySalesPhase.
**Migration**: Replaced by "The fan entering is the signed-in caller". The RPCs Apply and GetApplication become Create and Get on the lottery entry service.

### Requirement: Withdrawal names the phase, not the application
**Reason**: LotterySalesPhase is removed; a fan withdraws the entry for a TicketType.
**Migration**: Replaced by "Withdrawal names the ticket type, not the entry".

### Requirement: Lottery requests are validated at the boundary
**Reason**: Requests name a TicketType, and the identity rule is the User's personal details rule.
**Migration**: Replaced by "Lottery entry requests are validated at the boundary".
