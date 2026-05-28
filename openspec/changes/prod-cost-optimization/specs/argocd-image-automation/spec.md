## MODIFIED Requirements

### Requirement: Production deployments remain manual
The system SHALL NOT automatically update production environment deployments. The `argocd-image-updater-controller` Deployment SHALL NOT consume cluster resources in the prod cluster (its replicas SHALL be 0), and the prod argocd overlay SHALL NOT contain any ImageUpdater CR. Production image updates SHALL occur exclusively via manual semver-pinned overlay PRs.

#### Scenario: Prod image requires manual update
- **WHEN** a new image is released with semantic version tag (v1.2.3)
- **THEN** developer MUST manually update prod overlay kustomization with new version tag
- **THEN** production deployment SHALL only occur after manual kustomization commit

#### Scenario: Prod overlay has no ImageUpdater CR
- **WHEN** inspecting prod argocd overlay
- **THEN** overlay SHALL NOT contain an ImageUpdater CR
- **THEN** Image Updater SHALL ignore prod Applications entirely

#### Scenario: image-updater-controller is not running in prod cluster
- **WHEN** inspecting the prod argocd namespace
- **THEN** the `argocd-image-updater-controller` Deployment SHALL have `replicas: 0`
- **AND** no `argocd-image-updater-controller` Pod SHALL be running
- **AND** the Autopilot per-Pod billing for this controller SHALL be eliminated

#### Scenario: dev cluster continues to run image-updater
- **WHEN** inspecting the dev argocd namespace
- **THEN** the `argocd-image-updater-controller` Deployment SHALL run with its base replica count (1)
- **AND** dev Applications SHALL continue to receive automated digest updates
