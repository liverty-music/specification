## Why

The dev environment GKE Autopilot cluster costs ¥18,119/month (forecast), with Kubernetes Engine accounting for ¥4,910 (28%). Analysis of actual resource usage shows all workloads are over-provisioned by 5-50x on CPU and 2-17x on memory. Additionally, unused ArgoCD components (dex, notifications) are consuming resources, the backend runs unnecessary replicas for dev, and the concert-discovery CronJob is missing Spot VM scheduling.

## What Changes

- Reduce CPU/memory requests and limits for all workloads to match actual usage (with safety margin), leveraging GKE Autopilot Bursting support (confirmed: GKE 1.33)
- Disable ArgoCD dex-server (SSO not in use)
- Disable ArgoCD notifications-controller (notifications not configured)
- Reduce backend server replicas from 2 to 1 for dev environment
- Add Spot VM nodeSelector to concert-discovery CronJob (currently missing from patch target)

### Not in scope

- Gemini API cost reduction (¥6,496/month, 37% of total — separate investigation needed)
- Cloud Monitoring / Prometheus Samples Ingested optimization (¥2,034/month)
- Networking / Load Balancer cost reduction (¥2,103/month)
- Cloud SQL optimization (¥1,702/month)

## Capabilities

### New Capabilities

- `k8s-resource-right-sizing`: Defines resource request/limit policies for dev environment workloads based on actual usage data and GKE Autopilot constraints (Bursting minimum: 50m CPU / 52MiB memory)

### Modified Capabilities

- `continuous-delivery`: ArgoCD component configuration changes (disable dex, notifications) and dev overlay patching strategy update (CronJob Spot VM coverage)
- `deployment-infrastructure`: Backend replica count policy for dev environment; Spot VM nodeSelector coverage for all workload kinds

## Impact

- **K8s manifests**: `k8s/namespaces/argocd/base/values.yaml`, `k8s/namespaces/backend/`, `k8s/namespaces/frontend/`, `k8s/namespaces/external-secrets/`, `k8s/namespaces/reloader/` — all dev overlays
- **Cost**: Estimated 50-70% reduction in Kubernetes Engine costs (¥4,910 → ~¥1,500-2,500/month)
- **Risk**: Low — dev environment only, all changes are reversible, Bursting allows actual usage to exceed requests
