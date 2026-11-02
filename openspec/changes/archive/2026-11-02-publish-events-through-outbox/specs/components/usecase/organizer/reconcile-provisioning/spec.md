## MODIFIED Requirements

### Requirement: Completes every Organizer left provisioning

ReconcileProvisioning SHALL find the Organizers in status provisioning through Organizer.ListByStatus and complete each the way Create does, reusing the recorded Organization when there is one:

1. only when none is recorded, create the Organization through Organization.Create; when that fails with AlreadyExists, resolve it through Organization.GetByName, where NotFound fails with Internal and leaves the Organizer provisioning for the next run; then record it through Organizer.SetProviderOrganizerID;
2. complete it through Organization.Provision;
3. move the Organizer from provisioning to active through Organizer.CompareAndSetStatus.

#### Scenario: Organizer left provisioning

- **WHEN** an Organizer is provisioning after a failed Create
- **THEN** it becomes active, linked to one Organization with an owner identity

#### Scenario: Organization already recorded

- **WHEN** an Organizer left provisioning already has a recorded Organization
- **THEN** that Organization is completed and no other Organization is created

#### Scenario: Organization created but not recorded

- **WHEN** an earlier attempt created the Organization named by an Organizer's short name but did not record it, so Organization.Create fails with AlreadyExists
- **THEN** that Organization is found through Organization.GetByName, recorded and completed, no second Organization is created, and the Organizer becomes active

### Requirement: A deactivated Organizer is not reactivated

When an Organizer was deactivated while its provisioning was being completed, ReconcileProvisioning SHALL leave it deactivated.

#### Scenario: Deactivated meanwhile

- **WHEN** an Organizer is deactivated before ReconcileProvisioning moves it to active
- **THEN** it stays deactivated
