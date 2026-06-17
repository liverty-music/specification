# Argo CD Gateway Deployment

## Purpose

Defines the Argo CD Application topology for the platform — cluster-level, gateway-level, and backend Applications that sync independently — plus the prod-overlay Pod-count minimization (disabled image-updater / applicationset controllers, single argocd-server replica) used to bound Autopilot per-Pod cost.

## Requirements

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

### Requirement: Prod overlay minimizes Argo CD Pod count
The prod argocd overlay SHALL minimize the number of running Argo CD Pods by reducing the `argocd-server` replicas and disabling non-essential controllers, to keep GKE Autopilot per-Pod billing low.

#### Scenario: argocd-server runs with single replica in prod
- **WHEN** the prod cluster reconciles the argocd-server Deployment
- **THEN** the Deployment SHALL have `replicas: 1` (not 2)
- **AND** access to the Argo CD UI/API SHALL be unaffected at single-replica scale (no SLA on Argo CD UI HA is required in this phase)

#### Scenario: image-updater-controller replicas are 0 in prod
- **WHEN** the prod cluster reconciles the argocd-image-updater-controller Deployment
- **THEN** the Deployment SHALL have `replicas: 0`
- **AND** no Pod SHALL be running

#### Scenario: Disabled non-essential controllers are documented
- **WHEN** an operator reads the prod overlay
- **THEN** any Deployment patched to `replicas: 0` SHALL have a comment explaining why
- **AND** the comment SHALL state which capability/feature is being given up

### Requirement: dev overlay is unaffected
The dev environment overlay SHALL continue to run Argo CD with its default replica counts and all controllers enabled, to preserve dev iteration speed (image auto-update, notifications, applicationsets).

#### Scenario: dev overlay does not patch replicas
- **WHEN** the dev overlay is rendered
- **THEN** `argocd-server` SHALL keep its base replicas (`2` if base specifies HA, `1` if base specifies single)
- **AND** `argocd-image-updater-controller`, `argocd-notifications-controller`, and `argocd-applicationset-controller` SHALL keep their base replicas
