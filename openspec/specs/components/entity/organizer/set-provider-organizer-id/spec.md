# Organizer.SetProviderOrganizerID

## Purpose

Records the identity provider's ID for the Organization that provisioning created for an Organizer as the Organizer's provider organizer ID.

## Requirements

### Requirement: SetProviderOrganizerID links one Organization to one Organizer

SetProviderOrganizerID SHALL set the Organizer's provider organizer ID to the given Organization's ID, leaving its other attributes unchanged. Setting the ID the Organizer already has SHALL succeed. It SHALL fail with NotFound when the Organizer does not exist, and with AlreadyExists when another Organizer already has that provider organizer ID.

#### Scenario: Link is set

- **WHEN** the Organization is linked to no Organizer
- **THEN** the Organizer's provider organizer ID becomes that Organization's ID

#### Scenario: Same link again

- **WHEN** the Organizer is already linked to the same Organization
- **THEN** SetProviderOrganizerID succeeds and nothing changes

#### Scenario: Organization held by another Organizer

- **WHEN** another Organizer is already linked to the Organization
- **THEN** SetProviderOrganizerID fails with AlreadyExists

#### Scenario: Unknown Organizer

- **WHEN** no Organizer has the id
- **THEN** SetProviderOrganizerID fails with NotFound
