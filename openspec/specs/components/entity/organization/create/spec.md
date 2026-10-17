# Organization.Create

## Purpose

Creates the Organization of an Organizer, named by the Organizer's short name, so it can be recorded before provisioning continues.

## Requirements

### Requirement: Create makes one Organization named by the short name

Create SHALL create an Organization named by the given Organizer's short name and return it. It SHALL fail with AlreadyExists when an Organization with that name already exists, and create no second one. It SHALL fail with Internal when the Organization cannot be created for any other reason.

#### Scenario: First attempt

- **WHEN** Create runs for an Organizer with the short name `xx-records` and no Organization has that name
- **THEN** an Organization named `xx-records` is created and returned

#### Scenario: Name already used

- **WHEN** Create runs for the short name `xx-records` and an Organization named `xx-records` already exists
- **THEN** Create fails with AlreadyExists and creates no second Organization
