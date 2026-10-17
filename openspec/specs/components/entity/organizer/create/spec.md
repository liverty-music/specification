# Organizer.Create

## Purpose

Stores a new Organizer, normally in status provisioning, and returns the stored record.

## Requirements

### Requirement: Create stores the Organizer with its short name and owner email

Create SHALL store the Organizer with its id, name, short name, owner email, provider organizer ID and status, and SHALL return the stored Organizer. An Organizer given without an id SHALL receive a new one. It SHALL fail with AlreadyExists, storing nothing, when another Organizer, in any status, already has the short name. Create SHALL NOT deduplicate by name or owner email: an Organizer with the same name and owner email as an existing one but another short name is stored as a second Organizer.

#### Scenario: Organizer is stored

- **WHEN** a new provisioning Organizer is created
- **THEN** Create returns it as stored, with its short name and no provider organizer ID

#### Scenario: Same name and owner email twice

- **WHEN** an Organizer with the same name and owner email as an existing one but another short name is created
- **THEN** Create stores a second Organizer with a different id

#### Scenario: Short name already used

- **WHEN** an Organizer is created with the short name of an existing Organizer, even a deactivated one
- **THEN** Create fails with AlreadyExists and stores nothing
