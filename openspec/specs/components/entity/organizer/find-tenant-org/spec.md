# Organizer.FindTenantOrg

## Purpose

Finds an Organizer's sign-in tenant by its Organizer-derived name, for an Organizer whose provider organizer ID was never recorded.

## Requirements

### Requirement: The tenant is found by its exact name

FindTenantOrg SHALL return the Organization whose name is the given Organizer's short name, ignoring removed Organizations. It SHALL fail with NotFound when no such Organization exists, and with Internal when the Organizations cannot be searched.

#### Scenario: Tenant left by a failed attempt

- **WHEN** a first provisioning attempt created the Organizer's Organization but did not record it
- **THEN** FindTenantOrg returns that Organization, found by the Organizer's short name

#### Scenario: No tenant

- **WHEN** no Organization has the Organizer's short name
- **THEN** FindTenantOrg fails with NotFound
