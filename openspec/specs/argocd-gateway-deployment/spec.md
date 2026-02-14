## ADDED Requirements

### Requirement: Cluster-Level Application
The system SHALL define an ArgoCD Application that manages cluster-level resources (Namespaces) from `k8s/cluster/`.

#### Scenario: Cluster app deployed
- **WHEN** cluster-app Application is synced
- **THEN** namespaces (argocd, backend, gateway) are created in the cluster

#### Scenario: Namespace isolation ensured
- **WHEN** cluster-level resources are managed via ArgoCD
- **THEN** subsequent namespace-level applications can reference these namespaces

### Requirement: Gateway-Level Application
The system SHALL define an ArgoCD Application that manages Gateway infrastructure from `k8s/namespaces/gateway/overlays/dev/`.

#### Scenario: Gateway app deployed independently
- **WHEN** gateway-app Application is synced
- **WHEN** gateway namespace already exists (created by cluster-app)
- **THEN** Gateway, HTTPRoute, and Policy resources are created

#### Scenario: Gateway app does not trigger backend redeploy
- **WHEN** Gateway configuration changes (cert map, SSL policy)
- **THEN** only gateway resources are updated; backend Deployment is not redeployed

### Requirement: Backend Application
The system SHALL define an ArgoCD Application that manages backend resources from `k8s/namespaces/backend/overlays/dev/`.

#### Scenario: Backend app deployed
- **WHEN** backend-app Application is synced
- **THEN** Deployment, Service, and Policies (HealthCheck, Backend, Gateway) are created

#### Scenario: Backend app independent lifecycle
- **WHEN** backend Pod restarts or Deployment is updated
- **THEN** Gateway and HTTPRoute remain unchanged

### Requirement: GitOps Synchronization
The system SHALL automatically sync ArgoCD Applications when changes are committed to cloud-provisioning repository.

#### Scenario: Manual sync
- **WHEN** user runs `argocd app sync <app-name>`
- **THEN** manifests are deployed to cluster

#### Scenario: Automated sync (future)
- **WHEN** automated sync policy is enabled
- **THEN** ArgoCD continuously monitors repo and syncs drift

### Requirement: Application Dependency Ordering
The system SHALL define application sync order: cluster-app → gateway-app, backend-app (in parallel).

#### Scenario: Cluster created first
- **WHEN** cluster-app syncs successfully
- **THEN** gateway-app and backend-app can safely reference namespaces

#### Scenario: Gateway and backend independent
- **WHEN** gateway-app and backend-app both ready to sync
- **THEN** they can sync in any order without dependencies

### Requirement: Application Status Visibility
The system SHALL provide status of each application via `argocd app get <app-name>` and dashboard.

#### Scenario: Application status reported
- **WHEN** application is synced
- **THEN** status shows: Synced/OutOfSync, Healthy/Degraded, resources list

### Requirement: Rollback Capability
The system SHALL support rollback to previous application revision via ArgoCD.

#### Scenario: Rollback to previous config
- **WHEN** user runs `argocd app rollback <app-name> <revision>`
- **THEN** resources revert to previous configuration
