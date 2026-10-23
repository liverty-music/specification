## Purpose

Keeps every internet-facing API server except the admin console API from holding a credential that can change fan identities at the identity provider, so a compromise of the fan, organizer or reception API cannot take over fan accounts through the identity provider.

## ADDED Requirements

### Requirement: Only the admin console API and the event consumer hold an identity-provider credential

The fan, organizer and reception API servers SHALL run without any credential for the identity provider's management API; such a credential SHALL be neither mounted in them nor readable by them, including through a shared secret. Every change to a fan identity that the platform makes on its own (verification emails, passkey registration links) SHALL be made by the event consumer, and every change an admin makes SHALL be made by the admin console API. Each API server SHALL keep validating sign-in tokens with the identity provider's public keys, which are not a credential.

#### Scenario: API server deployment

- **WHEN** the fan, organizer or reception API is deployed
- **THEN** no identity-provider management credential is mounted in it or readable by it

#### Scenario: Fan requests a verification resend

- **WHEN** a signed-in fan requests a verification resend through the fan API
- **THEN** the fan API announces the request and the event consumer sends the code

#### Scenario: Signed-in calls keep working

- **WHEN** a caller calls a signed-in procedure of the fan, organizer or reception API with a valid token
- **THEN** the token is validated as before, without any identity-provider credential
