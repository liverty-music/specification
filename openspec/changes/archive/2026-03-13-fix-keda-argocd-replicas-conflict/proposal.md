## Why

KEDA ScaledObject (`minReplicaCount: 0`) and ArgoCD auto-sync (`selfHeal: true`) are fighting over the `consumer-app` Deployment's `replicas` field. The Deployment manifest hardcodes `replicas: 1`, but KEDA scales it to `0` when idle. ArgoCD detects the drift and syncs it back to `1`, KEDA immediately scales down again — creating an infinite loop (generation: 8871, selfHealAttempts: 38+). Image Updater exacerbates this by updating annotations every minute.

## What Changes

- Remove `replicas` field from `consumer-app` Deployment manifest so KEDA has sole ownership of replica count
- Add `ignoreDifferences` for `spec.replicas` on the `backend` ArgoCD Application as a safety net

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none — this is an infrastructure configuration fix, no spec-level behavior changes)

## Impact

- **cloud-provisioning**: `k8s/namespaces/backend/base/consumer/deployment.yaml` — remove `replicas: 1`
- **cloud-provisioning**: ArgoCD Application definition for `backend` — add `ignoreDifferences` for Deployment replicas
- **Risk**: Minimal. KEDA already records `originalReplicaCount: 1` and restores it if the ScaledObject is deleted
