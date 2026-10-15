# Spec Delta

## ADDED Requirements

### Requirement: Create stores, provisions and activates the Organizer

Create SHALL take a name, a short name and an owner email. It SHALL then:

1. store a new Organizer through Organizer.Create (it starts provisioning), failing with AlreadyExists and doing nothing else when the short name is already used;
2. create its Organization through Organizer.EnsureTenantOrg and record it at once through Organizer.SetProviderOrganizerID;
3. complete the Organization through Organizer.ProvisionTenant;
4. move the Organizer from provisioning to active through Organizer.CompareAndSetStatus.

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

When creating, recording or completing the Organization fails with AlreadyExists, InvalidArgument or FailedPrecondition, which retrying cannot fix, Create SHALL deactivate the Organizer through OrganizerUseCase.Deactivate, remove it and its Organization through OrganizerUseCase.Delete, and fail with the original error. When this clean-up fails, Create SHALL still fail with the original error, leaving at most a deactivated Organizer for an admin to delete.

#### Scenario: Owner email rejected during provisioning

- **WHEN** Organizer.ProvisionTenant fails with InvalidArgument because the sign-in service rejects the owner email
- **THEN** Create fails with InvalidArgument, and neither the Organizer nor its Organization remains

## REMOVED Requirements

### Requirement: Create checks the operator email, then stores, provisions and activates the Organizer

**Reason**: The email check against every Organization goes away; an email used by a fan account is allowed (see "Create stores, provisions and activates the Organizer").
**Migration**: None.

### Requirement: A permanent provisioning failure discards the Organizer

**Reason**: A taken email is no longer a provisioning failure; the requirement continues with a rejected email as its example (see "A permanent provisioning failure discards the new Organizer").
**Migration**: None.
