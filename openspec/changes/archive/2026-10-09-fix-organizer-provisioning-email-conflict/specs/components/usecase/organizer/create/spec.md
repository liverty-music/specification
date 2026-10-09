# Spec Delta

## REMOVED Requirements

### Requirement: Create stores, provisions and activates the Organizer

**Reason**: Its scenario "Same name and operator email again" no longer holds: the first Create makes the operator email a sign-in user, so a second Create with the same email fails with AlreadyExists.

**Migration**: Replaced by "Create checks the operator email, then stores, provisions and activates the Organizer", which keeps the same steps, adds the email check and early tenant recording, and covers repeated names with different emails.

## MODIFIED Requirements

### Requirement: A failed provisioning leaves the Organizer provisioning

When creating, recording or completing the tenant fails with Internal, Create SHALL fail with that error and leave the stored Organizer in status provisioning, keeping any recorded tenant; ReconcileProvisioning completes it later.

#### Scenario: Provisioning fails

- **WHEN** Organizer.ProvisionTenant fails with Internal
- **THEN** Create fails and the Organizer stays provisioning, linked to its tenant

## ADDED Requirements

### Requirement: Create checks the operator email, then stores, provisions and activates the Organizer

Create SHALL take a name and an initial operator email. It SHALL first check the email through Organizer.CheckOperatorEmailAvailable, and fail with that error, storing nothing, when the check fails. It SHALL then:

1. store a new Organizer through Organizer.Create (it starts provisioning);
2. create its tenant through Organizer.EnsureTenantOrg and record it at once through Organizer.SetZitadelOrgID;
3. complete the tenant through Organizer.ProvisionTenant;
4. move the Organizer from provisioning to active through Organizer.CompareAndSetStatus.

It SHALL return the created Organizer. Create does not look for an existing Organizer with the same name; an operator email can serve only one Organizer, because the first Create makes it a sign-in user.

#### Scenario: Organizer is created

- **WHEN** Create runs with a name and an operator email
- **THEN** the Organizer is active, linked to a new tenant in which the operator holds the owner role

#### Scenario: Same name again

- **WHEN** Create runs twice with the same name and two different operator emails
- **THEN** two Organizers exist, each with its own tenant

#### Scenario: Operator email used by another account

- **WHEN** Create runs with an operator email that another sign-in account already uses
- **THEN** it fails with AlreadyExists and no Organizer or tenant exists

### Requirement: A permanent provisioning failure discards the Organizer

When creating, recording or completing the tenant fails with AlreadyExists, InvalidArgument or FailedPrecondition, which retrying cannot fix, Create SHALL deactivate the Organizer through OrganizerUseCase.Deactivate, remove it and its tenant through OrganizerUseCase.Delete, and fail with the original error. When this clean-up fails, Create SHALL still fail with the original error, leaving at most a deactivated Organizer for an admin to delete.

#### Scenario: Operator email taken during provisioning

- **WHEN** Organizer.ProvisionTenant fails with AlreadyExists
- **THEN** Create fails with AlreadyExists, and neither the Organizer nor its tenant remains
