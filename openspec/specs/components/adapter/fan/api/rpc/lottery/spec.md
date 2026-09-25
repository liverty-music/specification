# Lottery RPC

## Purpose

The fan-facing lottery service boundary: every lottery call needs a signed-in fan, and the applicant is always the caller, never a fan named in the request.

## Requirements

### Requirement: The applicant is the signed-in caller

Every lottery call SHALL require a signed-in caller and fail with Unauthenticated otherwise. Apply, WithdrawApplication, GetMyApplication and GetResult SHALL resolve the caller to their stored User (User.GetByExternalID) and pass that User as the applicant to LotteryUseCase.Apply, WithdrawApplication, GetMyApplication and GetResult; the request never names an applicant. When the caller has no stored account, these calls SHALL fail with NotFound. CreateAuthorization only opens a card hold for a phase and ticket count, so it requires the sign-in but looks up no account and passes no applicant.

#### Scenario: Fan applies

- **WHEN** a signed-in fan calls Apply for a phase
- **THEN** the application is made with that fan as applicant

#### Scenario: Not signed in

- **WHEN** a caller who is not signed in calls GetResult
- **THEN** the call fails with Unauthenticated and no usecase runs

#### Scenario: Caller without an account

- **WHEN** a signed-in caller with no stored account calls Apply
- **THEN** the call fails with NotFound and nothing is applied

### Requirement: Withdrawal names the phase, not the application

WithdrawApplication SHALL take a phase; the boundary SHALL find the caller's own application for that phase with LotteryUseCase.GetMyApplication and withdraw it with LotteryUseCase.WithdrawApplication. When the caller has no application for the phase, the call SHALL fail with NotFound and nothing is withdrawn.

#### Scenario: Withdraw own application

- **WHEN** a fan with an application for the phase calls WithdrawApplication for it
- **THEN** that application is withdrawn

#### Scenario: No application

- **WHEN** a fan with no application for the phase calls WithdrawApplication
- **THEN** it fails with NotFound

### Requirement: Lottery requests are validated at the boundary

Every lottery call SHALL fail with InvalidArgument, before any usecase runs, when no phase is given. CreateAuthorization and Apply SHALL fail with InvalidArgument when the requested ticket count is not greater than 0; Apply SHALL also fail with InvalidArgument when the applicant's identity details or the card authorization are missing.

#### Scenario: Zero tickets

- **WHEN** Apply is called with a requested ticket count of 0
- **THEN** it fails with InvalidArgument and nothing is applied
