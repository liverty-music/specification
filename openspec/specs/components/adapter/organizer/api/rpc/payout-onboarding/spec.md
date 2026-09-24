# Organizer PayoutOnboardingService RPC

## Purpose

The organizer-facing payout onboarding boundary: it resolves the caller's own Organizer from their sign-in and returns that Organizer's payout-receiving account through OnboardingUseCase.GetOrCreateOnboarding.

## Requirements

### Requirement: The caller must be an operator of their own active Organizer

Every request SHALL carry a valid sign-in, or fail with Unauthenticated. The sign-in SHALL be issued for the organizer console and grant organizer-console roles in exactly one tenant, or the request fails with PermissionDenied. The boundary SHALL resolve the caller's Organizer through OrganizerUseCase.GetByZitadelOrgID with that tenant: when no Organizer is linked, or it is provisioning, the request SHALL fail with PermissionDenied without revealing whether an Organizer exists; when it is deactivated, the request SHALL fail with FailedPrecondition.

#### Scenario: Not signed in

- **WHEN** a request has no valid sign-in
- **THEN** it fails with Unauthenticated

#### Scenario: Roles in several tenants

- **WHEN** the sign-in grants organizer-console roles in two tenants
- **THEN** it fails with PermissionDenied

#### Scenario: Tenant with no Organizer

- **WHEN** no Organizer is linked to the caller's tenant
- **THEN** it fails with PermissionDenied

#### Scenario: Deactivated Organizer

- **WHEN** the caller's Organizer is deactivated
- **THEN** it fails with FailedPrecondition

### Requirement: GetPayoutOnboarding returns the caller's own account

GetPayoutOnboarding SHALL take no input, call OnboardingUseCase.GetOrCreateOnboarding for the caller's own Organizer, and return the account's reference and payout onboarding status, with the onboarding link only when one was returned. When the Organizer is no longer found, it SHALL fail with PermissionDenied.

#### Scenario: Operator opens payout settings

- **WHEN** an operator of an active Organizer calls GetPayoutOnboarding
- **THEN** it returns their Organizer's account and status, with an onboarding link while the account is not active

#### Scenario: Organizer gone meanwhile

- **WHEN** OnboardingUseCase.GetOrCreateOnboarding fails with NotFound
- **THEN** GetPayoutOnboarding fails with PermissionDenied
