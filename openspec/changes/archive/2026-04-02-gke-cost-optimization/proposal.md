## Why

GKE Autopilot's mandatory $0.10/hr cluster management fee (¥10,800/month) and Cloud NAT's fixed gateway cost (¥5,292/month) together account for ~¥16,000/month in unavoidable overhead on the dev environment — costs that can be eliminated by switching to a Standard zonal cluster with public nodes.

## What Changes

- **Replace** the GKE Autopilot cluster (`cluster-osaka`) with a Standard zonal cluster in `asia-northeast2-a`
  - New Spot node pool: `e2-standard-2`, min 1 / max 4 nodes
  - No cluster management fee (first zonal cluster in project is free)
- **Remove** Cloud NAT and Cloud Router from Pulumi (dev only)
  - Enable public nodes (`enablePrivateNodes: false`) to give nodes external IPs
  - All dependent services (Cloud SQL PSC, Secret Manager, Artifact Registry) are unaffected
- **Update** all Kubernetes nodeSelector patches from `cloud.google.com/compute-class: autopilot-spot` → `cloud.google.com/gke-spot: "true"` across dev overlays

## Capabilities

### New Capabilities

- `gke-standard-infrastructure`: Standard zonal GKE cluster with Spot node pool for dev, replacing Autopilot

### Modified Capabilities

- `deployment-infrastructure`: Node provisioning model changes from Autopilot (pod-based billing) to Standard (VM-based); Spot scheduling label changes
- `infra`: Cloud NAT and Cloud Router resources removed for dev environment

## Impact

- **cloud-provisioning/src/**: Pulumi GKE cluster definition, Cloud NAT/Router resources
- **cloud-provisioning/k8s/**: All dev overlay `spot-nodeselector-patch.yaml` files across namespaces
- **ArgoCD**: Target cluster endpoint changes after migration
- **Downtime**: Full cluster recreation required; dev downtime is acceptable
- **Cost**: ~¥16,000/month reduction in usage cost (GKE ¥10,800 + NAT ¥5,292)
