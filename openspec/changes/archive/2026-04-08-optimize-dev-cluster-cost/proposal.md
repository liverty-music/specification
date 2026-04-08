## Why

The dev GKE cluster costs significantly more than expected after migrating from Autopilot to Standard. The root cause is three compounding overheads: ADVANCED_DATAPATH (Dataplane V2 / `anetd`) consuming 195m CPU per node as a fixed DaemonSet cost, Google Managed Prometheus (GMP) adding DaemonSet collectors, and per-workload CPU requests set at 50m regardless of actual usage — forcing a second node when requests fill the first node's 1930m allocatable capacity.

## What Changes

- **Disable ADVANCED_DATAPATH** on the dev GKE cluster: switch from `ADVANCED_DATAPATH` to legacy `LEGACY_DATAPATH` (kube-proxy/iptables), eliminating the `anetd` DaemonSet (195m CPU/node)
- **Disable Google Managed Prometheus (GMP)**: add explicit `monitoringConfig.managedPrometheus.enabled: false` and restrict `loggingConfig`/`monitoringConfig` to `SYSTEM_COMPONENTS` only, removing GMP collector DaemonSets
- **Downsize node machine type**: change dev cluster node pool from `e2-standard-2` to `e2-medium` (2→0.94 allocatable vCPU, proportionally cheaper Spot pricing)
- **Reduce max node count**: lower `maxNodeCount` from 4 to 2 (dev workloads never need more than 2 nodes)
- **Right-size CPU requests across all workloads**: reduce from 50m to 10m for all dev pods (server-app, consumer-app, argocd components, keda, nats, otel-collector, external-secrets, atlas-operator, reloader, frontend caddy)
- **Set consumer-app ScaledObject maxReplicaCount to 1**: dev environment never needs horizontal scale-out for the consumer

## Capabilities

### New Capabilities

_(none — this is a pure infrastructure cost optimization with no new product capabilities)_

### Modified Capabilities

- `gke-standard-infrastructure`: cluster configuration changes — disable ADVANCED_DATAPATH, disable GMP, change machine type to e2-medium, reduce maxNodeCount to 2
- `k8s-resource-right-sizing`: extend right-sizing requirements to cover all system namespaces (argocd, keda, nats, otel-collector, external-secrets, atlas-operator, reloader) in dev overlays; reduce CPU floor from 50m to 10m; add maxReplicaCount=1 constraint for KEDA ScaledObjects in dev

## Impact

- **cloud-provisioning/src/gcp/components/kubernetes.ts**: modify dev cluster definition — remove `datapathProvider`, add `loggingConfig`, add `monitoringConfig` with GMP disabled, change machineType to `e2-medium`, maxNodeCount to 2
- **cloud-provisioning/k8s/namespaces/backend/overlays/dev/kustomization.yaml**: reduce server-app and consumer-app CPU requests to 10m; set ScaledObject maxReplicaCount to 1
- **cloud-provisioning/k8s/namespaces/argocd/overlays/dev/**: add resource patches for application-controller (20m CPU, 320Mi memory) and all other argocd components (10m CPU)
- **cloud-provisioning/k8s/namespaces/keda/overlays/dev/values.yaml**: reduce operator/metricServer/webhooks CPU requests to 10m
- **cloud-provisioning/k8s/namespaces/nats/overlays/dev/values.yaml**: reduce CPU requests to 10m
- **cloud-provisioning/k8s/namespaces/otel-collector/overlays/dev/kustomization.yaml**: reduce CPU requests to 10m
- **cloud-provisioning/k8s/namespaces/atlas-operator/overlays/dev/**: add CPU 10m patch
- **cloud-provisioning/k8s/namespaces/external-secrets/overlays/dev/**: reduce all 3 components to 10m CPU
- **cloud-provisioning/k8s/namespaces/reloader/overlays/dev/kustomization.yaml**: add CPU 10m patch
- **cloud-provisioning/k8s/namespaces/frontend/overlays/dev/kustomization.yaml**: reduce caddy CPU request to 10m
- **Cluster recreation required**: disabling ADVANCED_DATAPATH requires destroying and recreating the GKE cluster (in-place upgrade not supported); acceptable since the team has recently performed this operation
- **No monitoring impact**: all active alert policies are log-based (not GMP metrics-based), so disabling GMP has zero effect on production alerting
