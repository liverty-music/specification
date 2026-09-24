# Organizer.Create

## Purpose

Stores a new Organizer, normally in status provisioning, and returns the stored record.

## Requirements

### Requirement: Create stores the Organizer as given

Create SHALL store the Organizer with its id, name, operator email, tenant link and status, and SHALL return the stored Organizer. An Organizer given without an id SHALL receive a new one. Create SHALL NOT deduplicate: an Organizer with the same name and operator email as an existing one is stored as a second Organizer.

#### Scenario: Organizer is stored

- **WHEN** a new provisioning Organizer is created
- **THEN** Create returns it as stored, with no tenant link

#### Scenario: Same name and operator email twice

- **WHEN** an Organizer with the same name and operator email as an existing one is created
- **THEN** Create stores a second Organizer with a different id
