# continuous-delivery Specification

## Purpose

Defines the mechanism for GitOps-based continuous delivery using ArgoCD.

## Requirements

### Requirement: ArgoCD Manifests

The system SHALL provide Kustomize-based manifests for installing ArgoCD. The ArgoCD deployment SHALL NOT include the dex-server or notifications-controller components, as SSO and notification features are not in use.

#### Scenario: Manifest Availability

- **WHEN** checking the `src/k8s` directory
- **THEN** a `argocd` directory exists with a valid `kustomization.yaml`

#### Scenario: Unused components are disabled

- **WHEN** rendering the ArgoCD base manifests
- **THEN** dex-server SHALL NOT be deployed (dex.enabled: false)
- **AND** notifications-controller SHALL NOT be deployed (notifications.enabled: false)

### Requirement: Internal Web UI Access

The system SHALL provide access to the ArgoCD Web UI via secure internal channels (port-forwarding).

#### Scenario: Port Forward Access

- **WHEN** an administrator establishes a port-forward to the ArgoCD server service
- **THEN** they can access the Web UI on localhost
- **AND** the service is NOT exposed via an external LoadBalancer

### Requirement: Git Repository Integration

The system SHALL be configured to synchronize with the standard project repository.

#### Scenario: Public Repository Connection

- **WHEN** ArgoCD is running
- **THEN** it can successfully fetch manifests from `https://github.com/liverty-music/cloud-provisioning`

### Requirement: Root Application

The system SHALL include a Root Application definition to enable the App-of-Apps pattern.

#### Scenario: Root App Exists

- **WHEN** the setup is complete
- **THEN** an ArgoCD `Application` resource named `root-app` (or similar) exists
- **AND** it is configured to track the `main` branch of the project repository

### Requirement: Image Build and Publish

The system SHALL automatically build and publish a container image for the backend application when changes are pushed to the main branch.

#### Scenario: Push to Main

- **WHEN** a commit is merged to the `main` branch of `liverty-music/backend`
- **THEN** a GitHub Action triggers the build process
- **AND** a new container image with a unique tag is pushed to the Google Artifact Registry

### Requirement: Secure CI Authentication

The system SHALL utilize Workload Identity Federation (WIF) for authenticating the CI/CD pipeline to Google Cloud services, prohibiting the use of long-lived Service Account keys.

#### Scenario: Action Authentication

- **WHEN** the GitHub Action attempts to authenticate with GCP
- **THEN** it exchanges an OIDC token for a short-lived Google access token via the WIF provider
- **AND** it successfully gains permissions to write to the Artifact Registry

### Requirement: Backend Application Provisioning

The system SHALL include Kubernetes manifests for the backend application that are automatically synced by ArgoCD.

#### Scenario: App Config Exists

- **WHEN** the `cloud-provisioning` repository is inspected
- **THEN** a Kustomize base for the `backend` application exists
- **AND** it is referenced by the ArgoCD Root Application

### Requirement: ArgoCD SHALL sync Atlas migration resources from backend repo

The system SHALL include an ArgoCD Application that tracks the backend repository's `k8s/atlas/` directory for migration CRDs and ConfigMaps. This Application SHALL sync to the `atlas-operator` namespace.

#### Scenario: Migration ArgoCD Application

- **WHEN** ArgoCD reconciles the backend-migrations Application
- **THEN** it SHALL fetch manifests from `liverty-music/backend` repository
- **AND** the target path SHALL be `k8s/atlas/overlays/<env>`
- **AND** resources SHALL be deployed to the `atlas-operator` namespace

### Requirement: Migration sync wave SHALL precede application deployment

The AtlasMigration resource SHALL use ArgoCD sync wave annotations to ensure database migrations complete before the backend Deployment rolls out.

#### Scenario: Sync ordering

- **WHEN** ArgoCD performs a sync operation on the backend namespace
- **THEN** AtlasMigration resources SHALL sync before the backend Deployment
- **AND** the Deployment SHALL not start until migrations are applied
