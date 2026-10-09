# Organizer.EnsureTenantOrg

## Purpose

Creates an Organizer's sign-in tenant, or returns the tenant an earlier attempt for the same Organizer created, so the tenant can be recorded before provisioning continues.

## Requirements

### Requirement: One tenant per Organizer

EnsureTenantOrg SHALL return a sign-in tenant named after the Organizer, creating it when none exists. A repeated call for the same Organizer SHALL return the same tenant and create nothing new. It SHALL fail with Internal when the tenant can be neither created nor found.

#### Scenario: First attempt

- **WHEN** EnsureTenantOrg runs for an Organizer that has no tenant
- **THEN** a tenant named after the Organizer is created and returned

#### Scenario: Earlier attempt created the tenant

- **WHEN** EnsureTenantOrg runs again for the same Organizer
- **THEN** it returns the same tenant and creates no second one
