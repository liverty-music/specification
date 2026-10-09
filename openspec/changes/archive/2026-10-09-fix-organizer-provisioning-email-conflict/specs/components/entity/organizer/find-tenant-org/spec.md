# Spec Delta

## Purpose

Finds an Organizer's sign-in tenant by its Organizer-derived name, for an Organizer whose tenant link was never recorded.

## ADDED Requirements

### Requirement: The tenant is found by its exact name

FindTenantOrg SHALL return the tenant whose name is the one derived from the given Organizer, ignoring removed tenants. It SHALL fail with NotFound when no such tenant exists, and with Internal when the tenants cannot be searched.

#### Scenario: Tenant left by a failed attempt

- **WHEN** a first provisioning attempt created the Organizer's tenant but did not record it
- **THEN** FindTenantOrg returns that tenant

#### Scenario: No tenant

- **WHEN** no tenant has the Organizer's name
- **THEN** FindTenantOrg fails with NotFound
