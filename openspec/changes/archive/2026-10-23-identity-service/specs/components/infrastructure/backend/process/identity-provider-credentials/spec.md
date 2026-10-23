## RENAMED Requirements

- FROM: `### Requirement: Only the admin console API and the event consumer hold an identity-provider credential`
- TO: `### Requirement: Only the identity service holds an identity-provider credential`

## MODIFIED Requirements

### Requirement: Only the identity service holds an identity-provider credential

The identity service SHALL be the only backend process that holds a credential for the identity provider's management API. No other process SHALL have such a credential mounted or readable, including through a shared secret; this includes the fan, organizer, reception and admin console API servers and the event consumer.

Every change the platform makes to an identity at the identity provider SHALL be made by the identity service, on a request from another process:
- from the event consumer: verification emails and passkey registration links;
- from the admin console API: deleting a fan identity, and creating, provisioning, deactivating and deleting an Organizer's Organization.

The identity service SHALL take no requests from outside the cluster. Each calling process SHALL reach only the identity-service operations it uses, and every other process SHALL reach none. A request for an operation outside the caller's set SHALL be refused and SHALL change nothing. Each API server SHALL keep validating sign-in tokens with the identity provider's public keys, which are not a credential.

#### Scenario: API server deployment

- **WHEN** the fan, organizer, reception or admin console API or the event consumer is deployed
- **THEN** no identity-provider management credential is mounted in it or readable by it

#### Scenario: Fan requests a verification resend

- **WHEN** a signed-in fan requests a verification resend through the fan API
- **THEN** the fan API announces the request, the event consumer asks the identity service, and the identity service sends the code

#### Scenario: Admin deletes a fan

- **WHEN** an admin deletes a fan through the admin console API
- **THEN** the admin console API asks the identity service to delete the fan's identity

#### Scenario: Operation outside the caller's set

- **WHEN** the event consumer asks the identity service to delete a fan identity
- **THEN** the request is refused and the identity is unchanged

#### Scenario: Process with no access

- **WHEN** the fan API, or any process other than the event consumer and the admin console API, sends a request to the identity service
- **THEN** the request does not reach the identity service

#### Scenario: Request from outside the cluster

- **WHEN** a request from the internet is aimed at the identity service
- **THEN** it does not reach the identity service

#### Scenario: Signed-in calls keep working

- **WHEN** a caller calls a signed-in procedure of the fan, organizer or reception API with a valid token
- **THEN** the token is validated as before, without any identity-provider credential
