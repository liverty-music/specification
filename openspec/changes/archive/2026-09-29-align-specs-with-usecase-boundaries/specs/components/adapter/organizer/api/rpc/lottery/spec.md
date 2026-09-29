# Spec Delta

## MODIFIED Requirements

### Requirement: Every lottery call acts for the caller's own active Organizer

ConfigureLotteryPhase, GetLotteryPhaseStatus and SetPhaseVerificationRequirement SHALL pass the same organizer-console sign-in checks as the organizer Organizer service, and SHALL then resolve the caller's own Organizer through OrganizerUseCase.ResolveCaller with the caller's tenant. When the caller has no tenant, the call SHALL fail with PermissionDenied. A failure of ResolveCaller SHALL be returned unchanged: PermissionDenied when no Organizer is linked to the tenant or the Organizer is provisioning, and FailedPrecondition when it is deactivated. Only then SHALL the boundary call LotteryUseCase.ConfigureLotteryPhase, GetLotteryPhaseStatus or SetPhaseVerificationRequirement. That the event or phase belongs to the caller's Organizer is a precondition of the usecase, not of the boundary.

#### Scenario: Active Organizer configures a phase

- **WHEN** an operator of an active Organizer configures a lottery phase for its published event
- **THEN** the phase is configured and returned

#### Scenario: Tenant with no Organizer

- **WHEN** no Organizer is linked to the caller's tenant
- **THEN** the call fails with PermissionDenied and nothing is configured

#### Scenario: Deactivated Organizer

- **WHEN** the caller's Organizer is deactivated
- **THEN** the call fails with FailedPrecondition
