# Zitadel Service Account

## Purpose

Defines the Zitadel Machine User provisioning and Private Key JWT credential management for backend-to-Zitadel API communication.

## ADDED Requirements

### Requirement: Zitadel Machine User provisioned via Pulumi

The infrastructure SHALL provision a Zitadel Machine User (service account) via Pulumi for the backend to authenticate against the Zitadel Management API.

#### Scenario: Machine User creation

- **WHEN** the Pulumi stack is applied
- **THEN** a Zitadel Machine User SHALL exist with userName `backend-app`
- **AND** the Machine User SHALL have `ACCESS_TOKEN_TYPE_JWT` as its access token type

### Requirement: Private Key JWT credential

The Machine User SHALL be configured with a Private Key for JWT-based authentication. The key JSON file SHALL be stored in GCP Secret Manager.

#### Scenario: Key generation and storage

- **WHEN** the Pulumi stack is applied
- **THEN** a Machine Key SHALL be generated for the Machine User with type `KEY_TYPE_JSON`
- **AND** the key JSON content SHALL be stored in GCP Secret Manager as a secret
- **AND** the secret SHALL be named `zitadel-machine-key`

#### Scenario: Key mounted to backend pod via ESO

- **WHEN** the backend pod starts in GKE
- **THEN** External Secrets Operator SHALL sync the key from GCP Secret Manager to a Kubernetes Secret
- **AND** the key SHALL be mounted as a file at a configurable path in the backend container

### Requirement: Machine User IAM permissions

The Machine User SHALL be granted the minimum permissions required to send email verification codes.

#### Scenario: Required permissions

- **WHEN** the Machine User authenticates to the Zitadel API
- **THEN** the Machine User SHALL be able to call `POST /v2/users/{userId}/email/send`
- **AND** the Machine User SHALL be able to call `POST /v2/users/{userId}/email/resend`
- **AND** the Machine User SHALL NOT have broader admin permissions

### Requirement: Backend Zitadel API client configuration

The backend SHALL be configured with the Zitadel instance domain and the path to the Machine User's private key JSON file.

#### Scenario: Configuration via environment variables

- **WHEN** the backend starts
- **THEN** it SHALL read the Zitadel domain from the existing OIDC issuer configuration
- **AND** it SHALL read the key file path from `ZITADEL_MACHINE_KEY_PATH`
- **AND** it SHALL initialize the `zitadel-go/v3` client with `DefaultServiceUserAuthentication`

#### Scenario: Missing key file in development

- **WHEN** the backend starts in local development without a Zitadel key file configured
- **THEN** the Zitadel API client SHALL be nil/disabled
- **AND** the email verification consumer SHALL log a warning and skip processing
- **AND** the resend RPC SHALL return an error indicating the feature is unavailable
