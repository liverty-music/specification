# OrganizerUseCase.Create

## Purpose

OrganizerUseCase.Create registers a new Organizer from a name, a short name and an owner email and provisions its Organization with the owner identity, so the Organizer becomes active and its owner can sign in.

## Requirements

### Requirement: A failed provisioning leaves the Organizer provisioning

When creating, resolving, recording or completing the Organization fails with Internal, Create SHALL fail with that error and leave the stored Organizer in status provisioning, keeping any recorded Organization; ReconcileProvisioning completes it later.

#### Scenario: Provisioning fails

- **WHEN** Organization.Provision fails with Internal
- **THEN** Create fails and the Organizer stays provisioning, linked to its Organization

### Requirement: Deactivation during provisioning wins

When the Organizer was deactivated while its Organization was being provisioned, Create SHALL leave it deactivated, SHALL NOT announce it, and SHALL still succeed.

#### Scenario: Deactivated meanwhile

- **WHEN** the Organizer is deactivated before Create moves it to active
- **THEN** Create succeeds, the Organizer stays deactivated and no creation is announced

### Requirement: Activation is announced

When Create moves the Organizer to active, it SHALL announce that the Organizer was created. A failure to announce SHALL NOT fail Create.

#### Scenario: Organizer becomes active

- **WHEN** the Organizer is moved to active
- **THEN** its creation is announced

#### Scenario: Announcement fails

- **WHEN** the announcement cannot be made
- **THEN** Create still succeeds and the Organizer stays active

### Requirement: Create stores, provisions and activates the Organizer

Create SHALL take a name, a short name and an owner email. It SHALL then:

1. store a new Organizer through Organizer.Create (it starts provisioning), failing with AlreadyExists and doing nothing else when the short name is already used;
2. create its Organization through Organization.Create; when that fails with AlreadyExists, because an earlier attempt created the Organization but did not record it, resolve it through Organization.GetByName, where NotFound fails with Internal;
3. record the Organization at once through Organizer.SetProviderOrganizerID;
4. complete the Organization through Organization.Provision;
5. move the Organizer from provisioning to active through Organizer.CompareAndSetStatus.

It SHALL return the created Organizer. Create does not check the owner email against other Organizations: it may be the email of a fan account, an admin or another Organizer's owner. Create does not look for an existing Organizer with the same name.

#### Scenario: Organizer is created

- **WHEN** Create runs with a name and an owner email
- **THEN** the Organizer is active, linked to a new Organization in which the owner identity holds the owner role

#### Scenario: Same name again

- **WHEN** Create runs twice with the same name and two different short names
- **THEN** two Organizers exist, each with its own Organization named by its short name

#### Scenario: Short name already used

- **WHEN** Create runs with the short name of an existing Organizer
- **THEN** it fails with AlreadyExists and no Organizer or Organization is created

#### Scenario: Owner email of a fan account

- **WHEN** Create runs with an owner email that a fan account already uses
- **THEN** the Organizer is active, and its Organization holds a separate identity with that email

### Requirement: A permanent provisioning failure discards the new Organizer

When recording or completing the Organization fails with AlreadyExists, InvalidArgument or FailedPrecondition, which retrying cannot fix, Create SHALL deactivate the Organizer through OrganizerUseCase.Deactivate, remove it and its Organization through OrganizerUseCase.Delete, and fail with the original error. When this clean-up fails, Create SHALL still fail with the original error, leaving at most a deactivated Organizer for an admin to delete.

#### Scenario: Owner email rejected during provisioning

- **WHEN** Organization.Provision fails with InvalidArgument because the sign-in service rejects the owner email
- **THEN** Create fails with InvalidArgument, and neither the Organizer nor its Organization remains
