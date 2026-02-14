## ADDED Requirements

### Requirement: Image Updater monitors container registry
The system SHALL continuously monitor Google Artifact Registry (GAR) for new backend server images tagged with `latest`.

#### Scenario: New image digest detected
- **WHEN** a new backend image is pushed to GAR with tag `latest` and a different digest
- **THEN** Image Updater SHALL detect the digest change within 2 minutes

#### Scenario: No update for same digest
- **WHEN** an image is pushed with the same digest as currently deployed
- **THEN** Image Updater SHALL NOT create a new commit or trigger deployment

### Requirement: Automated kustomization updates for dev
The system SHALL automatically update the dev environment kustomization file with new image tags.

#### Scenario: Dev kustomization auto-updated
- **WHEN** Image Updater detects a new image digest for dev environment
- **THEN** system SHALL commit the updated kustomization.yaml to cloud-provisioning repo main branch
- **THEN** commit message SHALL include the image digest (sha256:...)
- **THEN** commit message SHALL be prefixed with "build:" for categorization

#### Scenario: Git write-back authentication
- **WHEN** Image Updater attempts to write to cloud-provisioning repo
- **THEN** system SHALL use ArgoCD's existing Git credentials
- **THEN** commit SHALL be attributed to a bot user (e.g., argocd-image-updater[bot])

### Requirement: Production deployments remain manual
The system SHALL NOT automatically update production environment kustomization files.

#### Scenario: Prod image requires manual update
- **WHEN** a new image is released with semantic version tag (v1.2.3)
- **THEN** Image Updater SHALL NOT update prod kustomization
- **THEN** developer MUST manually update prod overlay with new version tag
- **THEN** production deployment SHALL only occur after manual kustomization commit

### Requirement: Image pull policy enforcement
The system SHALL configure proper image pull policies for dev deployments.

#### Scenario: Always pull for latest tag
- **WHEN** dev deployment uses `latest` image tag
- **THEN** deployment spec SHALL set `imagePullPolicy: Always`
- **THEN** kubelet SHALL verify digest with registry on every pod creation
- **THEN** local cached image SHALL be used if digest matches

### Requirement: ArgoCD sync after kustomization update
The system SHALL trigger ArgoCD synchronization after Image Updater commits changes.

#### Scenario: Auto-sync enabled for dev
- **WHEN** Image Updater commits kustomization update to main branch
- **THEN** ArgoCD SHALL detect the Git change within 3 minutes (default sync interval)
- **THEN** ArgoCD SHALL automatically sync the dev application
- **THEN** new pods SHALL be created with updated image

#### Scenario: Dev application health check
- **WHEN** ArgoCD deploys new image to dev
- **THEN** Kubernetes health checks SHALL verify pod readiness
- **THEN** if health check fails, deployment SHALL NOT proceed
- **THEN** ArgoCD SHALL report Degraded health status

### Requirement: Audit trail for automated deployments
The system SHALL maintain a complete audit trail of all automated image updates.

#### Scenario: Git history shows all updates
- **WHEN** reviewing cloud-provisioning repo commit history
- **THEN** each automated image update SHALL have a distinct commit
- **THEN** commit message SHALL include image repository, tag, and digest
- **THEN** commits SHALL be filterable using "build:" prefix

#### Scenario: ArgoCD sync history tracking
- **WHEN** viewing ArgoCD application history
- **THEN** each automated sync SHALL be recorded with timestamp
- **THEN** sync details SHALL show Git commit SHA that triggered sync
- **THEN** previous syncs SHALL be available for rollback

### Requirement: Rollback capability
The system SHALL support rollback to previous image versions.

#### Scenario: Rollback via ArgoCD UI
- **WHEN** a deployed image causes issues in dev
- **THEN** operator SHALL rollback via ArgoCD application history
- **THEN** ArgoCD SHALL redeploy previous working version
- **THEN** rollback SHALL complete within 2 minutes

#### Scenario: Rollback via Git revert
- **WHEN** operator reverts Image Updater commit in cloud-provisioning repo
- **THEN** ArgoCD SHALL detect the revert commit
- **THEN** ArgoCD SHALL sync to the reverted kustomization
- **THEN** previous image version SHALL be redeployed

### Requirement: Update strategy configuration
The system SHALL use appropriate update strategies for image tag resolution.

#### Scenario: Latest tag strategy for dev
- **WHEN** configuring Image Updater for dev environment
- **THEN** update strategy SHALL be set to "latest"
- **THEN** Image Updater SHALL track the most recent image with latest tag
- **THEN** updates SHALL be based on digest changes, not tag changes

### Requirement: Failure handling and notifications
The system SHALL handle Image Updater failures gracefully.

#### Scenario: Registry connection failure
- **WHEN** Image Updater cannot connect to GAR
- **THEN** system SHALL log the error with details
- **THEN** Image Updater SHALL retry on next polling interval (2 minutes)
- **THEN** dev deployments SHALL continue using current image

#### Scenario: Git write-back failure
- **WHEN** Image Updater cannot commit to cloud-provisioning repo
- **THEN** system SHALL log authentication or permission error
- **THEN** Image Updater SHALL retry on next detection
- **THEN** operator SHALL be able to view error logs via kubectl

### Requirement: Environment isolation
The system SHALL maintain strict isolation between dev and prod automation.

#### Scenario: Dev Application has Image Updater enabled
- **WHEN** inspecting dev backend ArgoCD Application
- **THEN** Application SHALL have Image Updater annotations configured
- **THEN** annotations SHALL specify GAR image path and update strategy

#### Scenario: Prod Application has Image Updater disabled
- **WHEN** inspecting prod backend ArgoCD Application
- **THEN** Application SHALL NOT have Image Updater annotations
- **THEN** Image Updater SHALL ignore prod Application entirely
- **THEN** prod updates SHALL only occur via manual kustomization commits
