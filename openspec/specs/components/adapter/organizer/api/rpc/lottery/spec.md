# Organizer Lottery RPC

## Purpose

The organizer-facing lottery service boundary: how an operator's sign-in is turned into their own Organizer before a lottery phase is configured or read.

## Requirements

### Requirement: Every lottery call acts for the caller's own active Organizer

ConfigureLotteryPhase, GetLotteryPhaseStatus and SetPhaseVerificationRequirement SHALL pass the same organizer-console sign-in checks as the organizer Organizer service, and SHALL then resolve the caller's own Organizer through OrganizerUseCase.GetByZitadelOrgID with the caller's tenant. When the caller has no tenant, no Organizer is linked to it, or the Organizer is provisioning, the call SHALL fail with PermissionDenied. When the Organizer is deactivated, the call SHALL fail with FailedPrecondition. Only then SHALL the boundary call LotteryUseCase.ConfigureLotteryPhase, GetLotteryPhaseStatus or SetPhaseVerificationRequirement. That the event or phase belongs to the caller's Organizer is a precondition of the usecase, not of the boundary.

Known defect: liverty-music/backend#467

#### Scenario: Active Organizer configures a phase

- **WHEN** an operator of an active Organizer configures a lottery phase for its published event
- **THEN** the phase is configured and returned

#### Scenario: Tenant with no Organizer

- **WHEN** no Organizer is linked to the caller's tenant
- **THEN** the call fails with PermissionDenied and nothing is configured

#### Scenario: Deactivated Organizer

- **WHEN** the caller's Organizer is deactivated
- **THEN** the call fails with FailedPrecondition
