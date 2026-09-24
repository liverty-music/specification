# LotterySalesPhase.UpdateVerificationRequirement

## Purpose

Sets the verification requirement of one LotterySalesPhase and returns the updated phase.

## Requirements

### Requirement: Update the requirement

UpdateVerificationRequirement SHALL set the phase's verification requirement, leave its other attributes unchanged and return the updated phase. It SHALL fail with InvalidArgument when no phase id is given and with NotFound when no phase has the id.

#### Scenario: Requirement changed

- **WHEN** a phase's requirement None is updated to JPKI-only
- **THEN** the returned phase requires JPKI-only and its window, capacity and price are unchanged

#### Scenario: Unknown id

- **WHEN** no phase has the id
- **THEN** UpdateVerificationRequirement fails with NotFound
