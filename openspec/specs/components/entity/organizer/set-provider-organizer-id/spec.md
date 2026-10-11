# Organizer.SetProviderOrganizerID

## Purpose

Records the identity provider's ID for the sign-in tenant that provisioning created for an Organizer as the Organizer's provider organizer ID.

## Requirements

### Requirement: SetProviderOrganizerID links one tenant to one Organizer

SetProviderOrganizerID SHALL set the Organizer's provider organizer ID to the given tenant's ID, leaving its other attributes unchanged. Setting the ID the Organizer already has SHALL succeed. It SHALL fail with NotFound when the Organizer does not exist, and with AlreadyExists when another Organizer already has that provider organizer ID.

#### Scenario: Link is set

- **WHEN** the tenant is linked to no Organizer
- **THEN** the Organizer's provider organizer ID becomes that tenant's ID

#### Scenario: Same link again

- **WHEN** the Organizer is already linked to the same tenant
- **THEN** SetProviderOrganizerID succeeds and nothing changes

#### Scenario: Tenant held by another Organizer

- **WHEN** another Organizer is already linked to the tenant
- **THEN** SetProviderOrganizerID fails with AlreadyExists

#### Scenario: Unknown Organizer

- **WHEN** no Organizer has the id
- **THEN** SetProviderOrganizerID fails with NotFound
