# LotteryUseCase.SetPhaseVerificationRequirement

## Purpose

LotteryUseCase.SetPhaseVerificationRequirement lets an Organizer change whether applicants to a LotterySalesPhase must hold a verified identity.

## Requirements

### Requirement: Change the requirement at any time

SetPhaseVerificationRequirement SHALL set the phase's verification requirement with LotterySalesPhase.UpdateVerificationRequirement and return the updated phase, whether or not the window is open and whether or not the phase is drawn. It SHALL fail with InvalidArgument when no phase is given. Applications already made are not re-checked.

#### Scenario: Requirement tightened while open

- **WHEN** an Organizer sets JPKI-only on an open phase
- **THEN** the phase requires JPKI-only and later applications are checked against it

#### Scenario: After the draw

- **WHEN** an Organizer changes the requirement of a drawn phase
- **THEN** the requirement is changed

#### Scenario: Unknown phase

- **WHEN** the phase does not exist
- **THEN** SetPhaseVerificationRequirement fails with NotFound

### Requirement: Only the event's Organizer changes the requirement

SetPhaseVerificationRequirement SHALL fail with PermissionDenied when the calling Organizer does not own the phase's event.

#### Scenario: Another Organizer's phase

- **WHEN** an Organizer changes the requirement of a phase on an event owned by a different Organizer
- **THEN** SetPhaseVerificationRequirement fails with PermissionDenied and nothing changes
