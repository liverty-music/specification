# OrganizerUseCase.Create

## Purpose

OrganizerUseCase.Create registers a new Organizer from a name and an initial operator email and provisions its isolated sign-in tenant with that operator as owner, so the Organizer becomes active and its operator can sign in.

## Requirements

### Requirement: Create stores, provisions and activates the Organizer

Create SHALL take a name and an initial operator email, store a new Organizer with them through Organizer.Create (it starts provisioning), provision its tenant through Organizer.ProvisionTenant, record the tenant through Organizer.SetZitadelOrgID, and move the Organizer from provisioning to active through Organizer.CompareAndSetStatus. It SHALL return the created Organizer. Create does not look for an existing Organizer with the same name or operator email.

#### Scenario: Organizer is created

- **WHEN** Create runs with a name and an operator email
- **THEN** the Organizer is active, linked to a new tenant in which the operator holds the owner role

#### Scenario: Same name and operator email again

- **WHEN** Create runs twice with the same name and operator email
- **THEN** two Organizers exist, each with its own tenant

### Requirement: A failed provisioning leaves the Organizer provisioning

When Organizer.ProvisionTenant or Organizer.SetZitadelOrgID fails, Create SHALL fail with that error and leave the stored Organizer in status provisioning; ReconcileProvisioning completes it later.

#### Scenario: Provisioning fails

- **WHEN** Organizer.ProvisionTenant fails
- **THEN** Create fails and the Organizer stays provisioning

### Requirement: Deactivation during provisioning wins

When the Organizer was deactivated while its tenant was being provisioned, Create SHALL leave it deactivated, SHALL NOT announce it, and SHALL still succeed.

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
