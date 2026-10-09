# Spec Delta

## MODIFIED Requirements

### Requirement: Completes every Organizer left provisioning

ReconcileProvisioning SHALL find the Organizers in status provisioning through Organizer.ListByStatus and complete each the way Create does, reusing the recorded tenant when there is one:

1. create and record the tenant through Organizer.EnsureTenantOrg and Organizer.SetZitadelOrgID, only when none is recorded;
2. complete it through Organizer.ProvisionTenant;
3. move the Organizer from provisioning to active through Organizer.CompareAndSetStatus;
4. announce that the Organizer was created.

A failure to announce SHALL NOT count as a failure.

#### Scenario: Organizer left provisioning

- **WHEN** an Organizer is provisioning after a failed Create
- **THEN** it becomes active, linked to one tenant with an owner operator, and its creation is announced

#### Scenario: Tenant already recorded

- **WHEN** an Organizer left provisioning already has a recorded tenant
- **THEN** that tenant is completed and no other tenant is created

## ADDED Requirements

### Requirement: A permanent failure deactivates the Organizer

When completing an Organizer fails with AlreadyExists, InvalidArgument or FailedPrecondition, which retrying cannot fix, ReconcileProvisioning SHALL deactivate it through OrganizerUseCase.Deactivate so that later runs skip it, and SHALL NOT delete it. When the deactivation fails, the Organizer stays provisioning for the next run.

#### Scenario: Operator email taken

- **WHEN** an Organizer left provisioning fails to complete because its operator email belongs to another account
- **THEN** it becomes deactivated, its records are kept, and the next run does not try it again
