# Organizer.EnsureTenantOrg

## Purpose

Creates an Organizer's sign-in tenant, or returns the tenant an earlier attempt for the same Organizer created, so the tenant can be recorded before provisioning continues.

## Requirements

### Requirement: One tenant per Organizer

EnsureTenantOrg SHALL return an Organization named by the Organizer's short name, creating it when none exists. A repeated call for the same Organizer SHALL return the same Organization and create nothing new. It SHALL fail with Internal when the Organization can be neither created nor found.

#### Scenario: First attempt

- **WHEN** EnsureTenantOrg runs for an Organizer with the short name `xx-records` that has no Organization
- **THEN** an Organization named `xx-records` is created and returned

#### Scenario: Earlier attempt created the tenant

- **WHEN** EnsureTenantOrg runs again for the same Organizer
- **THEN** it returns the same Organization and creates no second one
