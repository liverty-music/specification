## ADDED Requirements

### Requirement: KEDA-managed Deployments SHALL NOT declare replicas

Deployments targeted by a KEDA ScaledObject SHALL omit `spec.replicas` from their Kustomize base manifest, delegating replica count management entirely to KEDA.

#### Scenario: Consumer Deployment with no replicas field
- **WHEN** the `consumer-app` Deployment manifest is rendered by Kustomize
- **THEN** the output SHALL NOT contain `spec.replicas`

### Requirement: ArgoCD SHALL ignore replicas drift for KEDA-managed Deployments

The ArgoCD Application for the `backend` namespace SHALL include `ignoreDifferences` for `spec.replicas` on Deployments managed by KEDA ScaledObjects.

#### Scenario: KEDA scales consumer to zero
- **WHEN** KEDA scales `consumer-app` to 0 replicas due to no active triggers
- **THEN** ArgoCD SHALL NOT report the Deployment as OutOfSync
