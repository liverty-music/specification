## ADDED Requirements

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

---

### Requirement: dev overlay is unaffected
The dev environment overlay SHALL continue to run Argo CD with its default replica counts and all controllers enabled, to preserve dev iteration speed (image auto-update, notifications, applicationsets).

#### Scenario: dev overlay does not patch replicas
- **WHEN** the dev overlay is rendered
- **THEN** `argocd-server` SHALL keep its base replicas (`2` if base specifies HA, `1` if base specifies single)
- **AND** `argocd-image-updater-controller`, `argocd-notifications-controller`, and `argocd-applicationset-controller` SHALL keep their base replicas
