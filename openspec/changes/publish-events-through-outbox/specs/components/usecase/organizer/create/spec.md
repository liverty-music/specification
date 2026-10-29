## MODIFIED Requirements

### Requirement: A failed provisioning leaves the Organizer provisioning

When creating, resolving, recording or completing the Organization fails with Internal, or moving the Organizer to active fails, Create SHALL fail with that error and leave the stored Organizer in status provisioning, keeping any recorded Organization; ReconcileProvisioning completes it later.

#### Scenario: Provisioning fails

- **WHEN** Organization.Provision fails with Internal
- **THEN** Create fails and the Organizer stays provisioning, linked to its Organization

#### Scenario: Activation fails

- **WHEN** Organizer.CompareAndSetStatus fails with Unavailable
- **THEN** Create fails with Unavailable and the Organizer stays provisioning, linked to its completed Organization

### Requirement: Deactivation during provisioning wins

When the Organizer was deactivated while its Organization was being provisioned, Create SHALL leave it deactivated and SHALL still succeed.

#### Scenario: Deactivated meanwhile

- **WHEN** the Organizer is deactivated before Create moves it to active
- **THEN** Create succeeds and the Organizer stays deactivated

## REMOVED Requirements

### Requirement: Activation is announced
**Reason**: Organizer.CompareAndSetStatus announces the Organizer's creation together with its move from provisioning to active (components/entity/organizer/compare-and-set-status), so the usecase no longer announces.
**Migration**: Product analytics receives the "organizer created" signal from Organizer.CompareAndSetStatus's announcement. A failure to announce now fails the activation, and Create fails with the Organizer left provisioning for ReconcileProvisioning.
