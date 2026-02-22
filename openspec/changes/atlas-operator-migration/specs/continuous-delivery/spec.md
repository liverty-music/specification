## ADDED Requirements

### Requirement: ArgoCD SHALL sync Atlas migration resources from backend repo

The system SHALL include an ArgoCD Application that tracks the backend repository's `k8s/atlas/` directory for migration CRDs and ConfigMaps. This Application SHALL sync to the `backend` namespace.

#### Scenario: Migration ArgoCD Application

- **WHEN** ArgoCD reconciles the backend-migrations Application
- **THEN** it SHALL fetch manifests from `liverty-music/backend` repository
- **AND** the target path SHALL be `k8s/atlas/overlays/<env>`
- **AND** resources SHALL be deployed to the `backend` namespace

### Requirement: Migration sync wave SHALL precede application deployment

The AtlasMigration resource SHALL use ArgoCD sync wave annotations to ensure database migrations complete before the backend Deployment rolls out.

#### Scenario: Sync ordering

- **WHEN** ArgoCD performs a sync operation on the backend namespace
- **THEN** AtlasMigration resources SHALL sync before the backend Deployment
- **AND** the Deployment SHALL not start until migrations are applied
