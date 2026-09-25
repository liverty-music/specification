# Spec Delta

## MODIFIED Requirements

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
