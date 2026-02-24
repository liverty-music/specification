### Requirement: Image Updater monitors container registry
The system SHALL continuously monitor Google Artifact Registry (GAR) for new container images tagged with `latest` at a 30-second polling interval.

#### Scenario: New image digest detected
- **WHEN** a new image is pushed to GAR with tag `latest` and a different digest
- **THEN** Image Updater SHALL detect the digest change within 30 seconds

#### Scenario: No update for same digest
- **WHEN** an image is pushed with the same digest as currently tracked
- **THEN** Image Updater SHALL NOT trigger any deployment

### Requirement: In-cluster parameter override for dev
The system SHALL update dev deployments by setting ArgoCD Application parameter overrides (kustomize images), without writing to Git.

#### Scenario: Dev Application parameter override updated
- **WHEN** Image Updater detects a new image digest for a dev Application
- **THEN** system SHALL call the ArgoCD API to set a kustomize image override on the Application resource
- **THEN** the override SHALL specify the new image digest
- **THEN** no commits SHALL be created in any Git repository

#### Scenario: ArgoCD syncs after parameter override
- **WHEN** the Application's kustomize image override is updated
- **THEN** ArgoCD SHALL detect the Application spec change
- **THEN** ArgoCD SHALL automatically sync the Application
- **THEN** new pods SHALL be created with the updated image

### Requirement: Parameter override recovery after Application recreation
The system SHALL recover automatically if ArgoCD Application parameter overrides are lost due to Application recreation.

#### Scenario: Application recreated by root-app sync
- **WHEN** root-app sync recreates a child Application and the kustomize image override is lost
- **THEN** Image Updater SHALL re-detect the latest digest within 30 seconds
- **THEN** Image Updater SHALL re-apply the parameter override
- **THEN** the Application SHALL return to the correct image within one polling cycle

### Requirement: Production deployments remain manual
The system SHALL NOT automatically update production environment deployments.

#### Scenario: Prod image requires manual update
- **WHEN** a new image is released with semantic version tag (v1.2.3)
- **THEN** Image Updater SHALL NOT update prod Application
- **THEN** developer MUST manually update prod overlay kustomization with new version tag
- **THEN** production deployment SHALL only occur after manual kustomization commit

#### Scenario: Prod overlay has no ImageUpdater CR
- **WHEN** inspecting prod argocd overlay
- **THEN** overlay SHALL NOT contain an ImageUpdater CR
- **THEN** Image Updater SHALL ignore prod Applications entirely

### Requirement: Image pull policy enforcement
The system SHALL configure proper image pull policies for dev deployments.

#### Scenario: Always pull for latest tag
- **WHEN** dev deployment uses `latest` image tag
- **THEN** deployment spec SHALL set `imagePullPolicy: Always`
- **THEN** kubelet SHALL verify digest with registry on every pod creation

### Requirement: Multiple image support
The system SHALL support automated updates for all dev container images.

#### Scenario: Backend server image auto-update
- **WHEN** a new backend server image is pushed to GAR
- **THEN** Image Updater SHALL update the backend ArgoCD Application

#### Scenario: Frontend web-app image auto-update
- **WHEN** a new frontend web-app image is pushed to GAR
- **THEN** Image Updater SHALL update the frontend ArgoCD Application

### Requirement: Rollback capability
The system SHALL support rollback to previous image versions.

#### Scenario: Rollback via ArgoCD UI
- **WHEN** a deployed image causes issues in dev
- **THEN** operator SHALL rollback via ArgoCD application history
- **THEN** ArgoCD SHALL redeploy previous working version

#### Scenario: Manual image override
- **WHEN** operator needs to pin a specific image version
- **THEN** operator SHALL use `argocd app set` to set a specific image override
- **THEN** Image Updater SHALL respect the manually set override until next digest change

### Requirement: Failure handling
The system SHALL handle Image Updater failures gracefully.

#### Scenario: Registry connection failure
- **WHEN** Image Updater cannot connect to GAR
- **THEN** system SHALL log the error with details
- **THEN** Image Updater SHALL retry on next polling interval (30 seconds)
- **THEN** dev deployments SHALL continue using current image

#### Scenario: ArgoCD API failure
- **WHEN** Image Updater cannot update ArgoCD Application parameter overrides
- **THEN** system SHALL log the error
- **THEN** Image Updater SHALL retry on next polling interval
- **THEN** operator SHALL be able to view error logs via kubectl
