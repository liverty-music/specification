# Spec Delta

## ADDED Requirements

### Requirement: A permanent failure deactivates the Organizer left provisioning

When completing an Organizer fails with AlreadyExists, InvalidArgument or FailedPrecondition, which retrying cannot fix, ReconcileProvisioning SHALL deactivate it through OrganizerUseCase.Deactivate so that later runs skip it, and SHALL NOT delete it. When the deactivation fails, the Organizer stays provisioning for the next run.

#### Scenario: Owner email rejected

- **WHEN** an Organizer left provisioning fails to complete because the sign-in service rejects its owner email
- **THEN** it becomes deactivated, its records are kept, and the next run does not try it again

## REMOVED Requirements

### Requirement: A permanent failure deactivates the Organizer

**Reason**: A taken email is no longer a provisioning failure; the requirement continues with a rejected email as its example (see "A permanent failure deactivates the Organizer left provisioning").
**Migration**: None.
