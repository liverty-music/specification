# Spec Delta

## MODIFIED Requirements

### Requirement: ProvisionTenant sets up the tenant and its owner

ProvisionTenant SHALL take an Organizer, its recorded sign-in tenant and the initial operator email. It SHALL make sure that the tenant's operators sign in to the organizer console with a passkey and no password, that the tenant may use the organizer console, and that the initial operator exists in the tenant with the owner role. The initial operator SHALL receive an invitation email whose link lets them register a passkey.

#### Scenario: Organizer is provisioned

- **WHEN** ProvisionTenant runs for an Organizer's tenant with an operator email
- **THEN** the operator holds the owner role in that tenant and is invited to register a passkey

### Requirement: ProvisionTenant is repeatable per Organizer

ProvisionTenant SHALL be keyed on the tenant: a repeated call SHALL NOT create a second initial operator, and a later call SHALL complete the steps that are missing. A tenant for which ProvisionTenant succeeded SHALL always have an operator holding the owner role. When the operator email belongs to a user outside the tenant, it SHALL fail with AlreadyExists. When the sign-in service rejects the email, it SHALL fail with InvalidArgument. When any other step fails, it SHALL fail with Internal.

#### Scenario: Repeated call

- **WHEN** ProvisionTenant runs again for a tenant it already provisioned
- **THEN** it creates nothing new

#### Scenario: Retry after a partial failure

- **WHEN** ProvisionTenant failed part-way and runs again for the same tenant
- **THEN** it completes the missing steps, and the operator holds the owner role

#### Scenario: Operator email used in another tenant

- **WHEN** the operator email belongs to a user of another tenant
- **THEN** ProvisionTenant fails with AlreadyExists and creates no operator
