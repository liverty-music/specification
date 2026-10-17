# Organization.GetByName

## Purpose

Returns an Organizer's Organization by its name, the Organizer's short name, for an Organizer whose provider organizer ID was never recorded.

## Requirements

### Requirement: The Organization is found by its exact name

GetByName SHALL return the Organization whose name is the given Organizer's short name, ignoring removed Organizations. It SHALL fail with NotFound when no such Organization exists, and with Internal when the Organizations cannot be searched.

#### Scenario: Organization left by a failed attempt

- **WHEN** a first provisioning attempt created the Organizer's Organization but did not record it
- **THEN** GetByName returns that Organization, found by the Organizer's short name

#### Scenario: No Organization

- **WHEN** no Organization has the Organizer's short name
- **THEN** GetByName fails with NotFound
