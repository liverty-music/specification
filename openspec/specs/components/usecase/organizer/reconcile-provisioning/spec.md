# OrganizerUseCase.ReconcileProvisioning

## Purpose

OrganizerUseCase.ReconcileProvisioning finishes provisioning for every Organizer left in status provisioning, for example after a failed Create, so each eventually becomes active with an owner operator.

## Requirements

### Requirement: Runs every 5 minutes

ReconcileProvisioning SHALL run every 5 minutes, the first run 5 minutes after the service starts.

#### Scenario: Scheduled run

- **WHEN** 5 minutes have passed since the previous run
- **THEN** ReconcileProvisioning runs

### Requirement: Completes every Organizer left provisioning

ReconcileProvisioning SHALL find the Organizers in status provisioning through Organizer.ListByStatus and complete each the way Create does: Organizer.ProvisionTenant, Organizer.SetZitadelOrgID, Organizer.CompareAndSetStatus from provisioning to active, then announce that the Organizer was created. A failure to announce SHALL NOT count as a failure.

#### Scenario: Organizer left provisioning

- **WHEN** an Organizer is provisioning after a failed Create
- **THEN** it becomes active, linked to one tenant with an owner operator, and its creation is announced

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
