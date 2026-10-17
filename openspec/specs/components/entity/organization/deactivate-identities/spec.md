# Organization.DeactivateIdentities

## Purpose

Stops every member of an Organizer from signing in to the Organizer's Organization, by turning off their identities.

## Requirements

### Requirement: DeactivateIdentities turns off every identity in the Organization

DeactivateIdentities SHALL make every identity in the given Organization unable to sign in: an identity that has signed in before is deactivated, and an identity whose member never completed their first sign-in is removed. Identities already turned off SHALL count as done, so a repeated call succeeds. When an identity cannot be turned off it SHALL fail with Internal; identities already turned off stay off.

#### Scenario: Organization with identities

- **WHEN** the Organization has an identity that has signed in and one whose member never accepted the invitation
- **THEN** the first is deactivated, the second is removed, and neither can sign in

#### Scenario: Repeated call

- **WHEN** every identity in the Organization is already turned off
- **THEN** DeactivateIdentities succeeds and nothing changes
