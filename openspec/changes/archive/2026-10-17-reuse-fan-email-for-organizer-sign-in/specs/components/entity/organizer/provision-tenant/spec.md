# Spec Delta

## ADDED Requirements

### Requirement: ProvisionTenant sets up the Organization and its owner

ProvisionTenant SHALL take an Organizer, its recorded Organization and the owner email. It SHALL make sure that:

- the Organization's identities sign in to the organizer console with a passkey and no password, by typing their email;
- the Organization tells a person who types an email that names no identity there that it is unknown, instead of continuing as if it existed;
- the Organization may use the organizer console;
- an identity exists in the Organization with the owner email as its email, the user name `<owner email> (<short name>)` and the owner role.

That identity SHALL receive an invitation email whose link lets them register a passkey. The owner email MAY already be the email of an identity in another Organization - a fan account, an admin or another Organizer's owner - and that identity is neither used nor changed.

#### Scenario: Organizer is provisioned

- **WHEN** ProvisionTenant runs for the Organizer `xx-records` with the owner email `band@example.com`
- **THEN** an identity with the email `band@example.com` and the user name `band@example.com (xx-records)` holds the owner role in that Organization and is invited to register a passkey

#### Scenario: Owner email of a fan account

- **WHEN** the owner email is the email of a fan account
- **THEN** a separate identity with that email is created in the Organizer's Organization and the fan account is unchanged

### Requirement: ProvisionTenant is repeatable for the Organization

ProvisionTenant SHALL be keyed on the Organization: a repeated call SHALL NOT create a second owner identity, and a later call SHALL complete the steps that are missing. An Organization for which ProvisionTenant succeeded SHALL always have an identity holding the owner role. When the sign-in service rejects the email or the user name, it SHALL fail with InvalidArgument. When any other step fails, it SHALL fail with Internal.

#### Scenario: Repeated call

- **WHEN** ProvisionTenant runs again for an Organization it already provisioned
- **THEN** it creates nothing new

#### Scenario: Retry after a partial failure

- **WHEN** ProvisionTenant failed part-way and runs again for the same Organization
- **THEN** it completes the missing steps, and the owner identity holds the owner role

#### Scenario: Email rejected by the sign-in service

- **WHEN** the sign-in service rejects the owner email
- **THEN** ProvisionTenant fails with InvalidArgument and creates no identity

## REMOVED Requirements

### Requirement: ProvisionTenant sets up the tenant and its owner

**Reason**: The owner identity's user name is `<owner email> (<short name>)` so the email can be shared with other accounts, and the Organization reports unknown emails so a passkey sign-in typed by email completes (see "ProvisionTenant sets up the Organization and its owner").
**Migration**: The existing Organization's login policy and identity user names are updated once (design.md Migration Plan).

### Requirement: ProvisionTenant is repeatable per Organizer

**Reason**: An email used in another Organization no longer fails provisioning, because user names include the short name (see "ProvisionTenant is repeatable for the Organization").
**Migration**: None.
