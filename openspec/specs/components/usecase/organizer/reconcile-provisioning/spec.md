# OrganizerUseCase.ReconcileProvisioning

## Purpose

OrganizerUseCase.ReconcileProvisioning finishes provisioning for every Organizer left in status provisioning, for example after a failed Create, so each eventually becomes active with an owner identity.

## Requirements

### Requirement: Runs every 5 minutes

ReconcileProvisioning SHALL run every 5 minutes, the first run 5 minutes after the service starts.

#### Scenario: Scheduled run

- **WHEN** 5 minutes have passed since the previous run
- **THEN** ReconcileProvisioning runs

### Requirement: Completes every Organizer left provisioning

ReconcileProvisioning SHALL find the Organizers in status provisioning through Organizer.ListByStatus and complete each the way Create does, reusing the recorded Organization when there is one:

1. only when none is recorded, create the Organization through Organization.Create; when that fails with AlreadyExists, resolve it through Organization.GetByName, where NotFound fails with Internal and leaves the Organizer provisioning for the next run; then record it through Organizer.SetProviderOrganizerID;
2. complete it through Organization.Provision;
3. move the Organizer from provisioning to active through Organizer.CompareAndSetStatus;
4. announce that the Organizer was created.

A failure to announce SHALL NOT count as a failure.

#### Scenario: Organizer left provisioning

- **WHEN** an Organizer is provisioning after a failed Create
- **THEN** it becomes active, linked to one Organization with an owner identity, and its creation is announced

#### Scenario: Organization already recorded

- **WHEN** an Organizer left provisioning already has a recorded Organization
- **THEN** that Organization is completed and no other Organization is created

#### Scenario: Organization created but not recorded

- **WHEN** an earlier attempt created the Organization named by an Organizer's short name but did not record it, so Organization.Create fails with AlreadyExists
- **THEN** that Organization is found through Organization.GetByName, recorded and completed, no second Organization is created, and the Organizer becomes active

### Requirement: One failure does not stop the others

When completing one Organizer fails, ReconcileProvisioning SHALL leave it provisioning for the next run and continue with the rest.

#### Scenario: One Organizer fails

- **WHEN** two Organizers are provisioning and provisioning the first fails
- **THEN** the second becomes active and the first stays provisioning

### Requirement: A deactivated Organizer is not reactivated

When an Organizer was deactivated while its provisioning was being completed, ReconcileProvisioning SHALL leave it deactivated and not announce it.

#### Scenario: Deactivated meanwhile

- **WHEN** an Organizer is deactivated before ReconcileProvisioning moves it to active
- **THEN** it stays deactivated

### Requirement: The run fails when the Organizers cannot be listed

When Organizer.ListByStatus fails, ReconcileProvisioning SHALL fail and change nothing; the next run tries again.

#### Scenario: Listing fails

- **WHEN** Organizer.ListByStatus fails
- **THEN** ReconcileProvisioning fails and no Organizer changes

### Requirement: A permanent failure deactivates the Organizer left provisioning

When completing an Organizer fails with AlreadyExists, InvalidArgument or FailedPrecondition, which retrying cannot fix, ReconcileProvisioning SHALL deactivate it through OrganizerUseCase.Deactivate so that later runs skip it, and SHALL NOT delete it. When the deactivation fails, the Organizer stays provisioning for the next run.

#### Scenario: Owner email rejected

- **WHEN** an Organizer left provisioning fails to complete because the sign-in service rejects its owner email
- **THEN** it becomes deactivated, its records are kept, and the next run does not try it again
