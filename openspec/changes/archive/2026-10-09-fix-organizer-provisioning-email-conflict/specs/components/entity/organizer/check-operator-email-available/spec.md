# Spec Delta

## Purpose

Tells whether an email can become the initial operator of a new Organizer's sign-in tenant. Sign-in user names are unique across all tenants and default to the email.

## ADDED Requirements

### Requirement: An email used by any sign-in user is not available

CheckOperatorEmailAvailable SHALL succeed when no sign-in user in any tenant has the given email as their email, user name or login name, compared without regard to letter case. It SHALL fail with AlreadyExists otherwise, and with Internal when the users cannot be searched.

#### Scenario: Unused email

- **WHEN** no sign-in user has the email
- **THEN** CheckOperatorEmailAvailable succeeds

#### Scenario: Email of the platform administrator

- **WHEN** the instance administrator, who belongs to another tenant, has the email as their user name
- **THEN** CheckOperatorEmailAvailable fails with AlreadyExists

#### Scenario: Different letter case

- **WHEN** a user has the email `Operator@Example.com` and `operator@example.com` is checked
- **THEN** CheckOperatorEmailAvailable fails with AlreadyExists
