## MODIFIED Requirements

### Requirement: ArgoCD Manifests

The system SHALL provide Kustomize-based manifests for installing ArgoCD. The ArgoCD deployment SHALL NOT include the dex-server or notifications-controller components, as SSO and notification features are not in use.

#### Scenario: Manifest Availability

- **WHEN** checking the `src/k8s` directory
- **THEN** a `argocd` directory exists with a valid `kustomization.yaml`

#### Scenario: Unused components are disabled

- **WHEN** rendering the ArgoCD base manifests
- **THEN** dex-server SHALL NOT be deployed (dex.enabled: false)
- **AND** notifications-controller SHALL NOT be deployed (notifications.enabled: false)
