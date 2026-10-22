## Purpose

Keeps the internet-facing fan API from holding any credential that can change fan identities at the identity provider, so a compromise of the fan API cannot take over fan accounts through the identity provider.

## ADDED Requirements

### Requirement: The fan API holds no identity-provider credential

The fan API server SHALL run without any credential for the identity provider's management API. Every change to a fan identity that the platform makes on its own (verification emails, passkey registration links) SHALL be made by the event consumer, and every change an admin makes SHALL be made by the admin console API. The fan API SHALL keep validating fans' sign-in tokens with the identity provider's public keys, which are not a credential.

#### Scenario: Fan API deployment

- **WHEN** the fan API is deployed
- **THEN** no identity-provider management credential is mounted in it or readable by it

#### Scenario: Fan requests a verification resend

- **WHEN** a signed-in fan requests a verification resend through the fan API
- **THEN** the fan API announces the request and the event consumer sends the code

#### Scenario: Signed-in calls keep working

- **WHEN** a fan calls a signed-in fan API procedure with a valid token
- **THEN** the token is validated as before, without any identity-provider credential
