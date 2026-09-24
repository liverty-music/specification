# Organizer.ProvisionTenant

## Purpose

Gives an Organizer its isolated sign-in tenant, with the initial operator as the tenant's owner, and returns that tenant.

## Requirements

### Requirement: ProvisionTenant sets up the tenant and its owner

ProvisionTenant SHALL, for the given Organizer, make sure that a sign-in tenant exists for it, that the tenant's operators sign in to the organizer console with a passkey and no password, that the tenant may use the organizer console, and that the initial operator exists in the tenant with the owner role. The initial operator SHALL receive an invitation email whose link lets them register a passkey. It SHALL return the tenant.

#### Scenario: Organizer is provisioned

- **WHEN** ProvisionTenant runs for an Organizer with a name and an operator email
- **THEN** it returns the Organizer's tenant, in which the operator holds the owner role and is invited to register a passkey

### Requirement: ProvisionTenant is repeatable per Organizer

ProvisionTenant SHALL be keyed on the Organizer: a repeated call for the same Organizer SHALL return the same tenant and SHALL NOT create a second tenant or a second initial operator. When a step fails it SHALL fail with Internal; a later call SHALL complete the steps that are missing. A tenant for which ProvisionTenant succeeded SHALL always have an operator holding the owner role.

#### Scenario: Repeated call

- **WHEN** ProvisionTenant runs again for an Organizer it already provisioned
- **THEN** it returns the same tenant and creates nothing new

#### Scenario: Retry after a partial failure

- **WHEN** ProvisionTenant failed after creating the tenant and runs again for the same Organizer
- **THEN** it completes the missing steps without a second tenant, and the operator holds the owner role
