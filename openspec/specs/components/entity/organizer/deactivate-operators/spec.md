# Organizer.DeactivateOperators

## Purpose

Stops every operator of an Organizer's tenant from signing in.

## Requirements

### Requirement: DeactivateOperators turns off every operator of the tenant

DeactivateOperators SHALL make every operator in the given tenant unable to sign in: an operator who has signed in before is deactivated, and an operator who never completed their first sign-in is removed. Operators already turned off SHALL count as done, so a repeated call succeeds. When an operator cannot be turned off it SHALL fail with Internal; operators already turned off stay off.

#### Scenario: Tenant with operators

- **WHEN** the tenant has an operator who has signed in and one who never accepted the invitation
- **THEN** the first is deactivated, the second is removed, and neither can sign in

#### Scenario: Repeated call

- **WHEN** every operator of the tenant is already turned off
- **THEN** DeactivateOperators succeeds and nothing changes
