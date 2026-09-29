# Spec Delta

## Purpose

OrganizerUseCase.ResolveCaller turns an organizer-console operator's sign-in tenant into their own Organizer and admits it only while it is active, so every organizer-facing call acts for an Organizer that serves its operators.

## ADDED Requirements

### Requirement: Only an active Organizer is resolved

ResolveCaller SHALL read the Organizer linked to the tenant (Organizer.GetByZitadelOrgID) and return it when it is active. When no Organizer is linked to the tenant, or the Organizer is in any status other than active and deactivated, such as provisioning, ResolveCaller SHALL fail with PermissionDenied without revealing whether an Organizer exists. When the Organizer is deactivated, ResolveCaller SHALL fail with FailedPrecondition and may say that the Organizer is deactivated, since it is the caller's own. Any other failure to read the Organizer SHALL be returned unchanged.

#### Scenario: Active Organizer

- **WHEN** the tenant is linked to an active Organizer
- **THEN** ResolveCaller returns that Organizer

#### Scenario: Tenant with no Organizer

- **WHEN** no Organizer is linked to the tenant
- **THEN** ResolveCaller fails with PermissionDenied and does not reveal whether an Organizer exists

#### Scenario: Provisioning Organizer

- **WHEN** the tenant's Organizer is provisioning
- **THEN** ResolveCaller fails with PermissionDenied

#### Scenario: Deactivated Organizer

- **WHEN** the tenant's Organizer is deactivated
- **THEN** ResolveCaller fails with FailedPrecondition

#### Scenario: Organizer unreadable

- **WHEN** reading the Organizer fails with Internal
- **THEN** ResolveCaller fails with Internal
