# Spec Delta

## Purpose

User.HasIdentity reports whether the sign-in identity a User is linked to still exists, so an account left behind by a removed identity can be told apart from one in use.

## ADDED Requirements

### Requirement: HasIdentity reports whether the identity exists

HasIdentity SHALL take a provider user ID and report true when the identity provider holds an identity with that ID, whatever its state, and false only when the identity provider answers that no such identity exists. It SHALL fail with InvalidArgument when the ID is empty. When it cannot get an answer it SHALL fail with Unavailable when the identity provider cannot be reached and Internal otherwise, and SHALL NOT report false.

#### Scenario: Existing identity

- **WHEN** HasIdentity runs for an identity that can sign in
- **THEN** it reports true

#### Scenario: Deactivated identity

- **WHEN** HasIdentity runs for a deactivated identity
- **THEN** it reports true

#### Scenario: Removed identity

- **WHEN** HasIdentity runs for an identity that was removed
- **THEN** it reports false

#### Scenario: Provider unreachable

- **WHEN** the identity provider cannot be reached
- **THEN** HasIdentity fails with Unavailable and reports nothing

#### Scenario: Empty ID

- **WHEN** the provider user ID is empty
- **THEN** HasIdentity fails with InvalidArgument
