## Context

The `backend` ArgoCD Application manages the `consumer-app` Deployment with `replicas: 1` in the Kustomize base manifest. KEDA ScaledObject targets the same Deployment with `minReplicaCount: 0`, scaling to zero when the NATS JetStream trigger is inactive. ArgoCD's `selfHeal: true` continuously restores `replicas: 1`, creating an infinite reconciliation loop.

Current state:
- `k8s/namespaces/backend/base/consumer/deployment.yaml`: `spec.replicas: 1`
- ScaledObject: `minReplicaCount: 0`, `cooldownPeriod: 300`
- ArgoCD: `automated.selfHeal: true`
- Observed: Deployment generation 8871+, selfHealAttempts 38+

## Goals / Non-Goals

**Goals:**
- Eliminate the ArgoCD ↔ KEDA reconciliation loop for `consumer-app`
- Let KEDA have sole ownership of `replicas` for Deployments managed by ScaledObjects

**Non-Goals:**
- Changing KEDA scaling parameters (min/max replicas, triggers)
- Modifying ArgoCD sync policy globally

## Decisions

### 1. Remove `replicas` from Deployment manifest

Remove `spec.replicas` from `consumer/deployment.yaml`. When omitted, Kubernetes defaults to `1` on first creation, and KEDA immediately takes over via HPA. This is the [recommended pattern from KEDA docs](https://keda.sh/docs/2.16/concepts/scaling-deployments/#details).

**Alternative considered**: Set `replicas: 0` in manifest. Rejected because it would cause a brief outage on every ArgoCD sync before KEDA scales up.

### 2. Add `ignoreDifferences` for replicas on backend Application

Add `ignoreDifferences` to the `backend` ArgoCD Application spec as a defense-in-depth measure:

```yaml
spec:
  ignoreDifferences:
  - group: apps
    kind: Deployment
    name: consumer-app
    jsonPointers:
    - /spec/replicas
```

This ensures ArgoCD never considers `replicas` drift as OutOfSync, even if someone accidentally re-adds `replicas` to the manifest.

**Where to configure**: In the root-app Application definition in `cloud-provisioning` that generates the `backend` Application, or directly on the Application resource.

## Risks / Trade-offs

- **[Risk] KEDA removed without replicas field** → Kubernetes defaults to `1` replica; KEDA also stores `originalReplicaCount: 1` and restores it on ScaledObject deletion. Low risk.
- **[Risk] ignoreDifferences too broad** → Scoped to `consumer-app` Deployment only, not all Deployments. Acceptable.
