## Why

The previous change `optimize-dev-gke-cost` (archived 2026-04-28) only realized ~38% of the targeted Compute Engine cost reduction. Post-deploy investigation pinpointed the gap: total CPU requests across the dev spot pool sit at 2288m on 3 e2-medium nodes, exceeding the 2-node ceiling (1880m) by 408m. The dominant non-DaemonSet consumer is `kube-dns × 2 replicas = 540m`, kept at 2 replicas by `preventSinglePointFailure: true` in the GKE-managed `kube-dns-autoscaler` ConfigMap. With the cluster-proportional-autoscaler formula (`coresPerReplica: 256, nodesPerReplica: 16`), the calculated replica count for our 3-node, 6-vCPU dev cluster would otherwise be `max(6/256, 3/16, 1) = 1`. Disabling the single-point-of-failure guard frees ~270m, lets the cluster autoscaler retire the 3rd spot node, and completes the cost-optimization that boot-disk shrink + Zitadel replica drops alone could not.

## What Changes

- Add a dev-only Kubernetes manifest declaring the `kube-dns-autoscaler` ConfigMap (in `kube-system`) with `preventSinglePointFailure: false`, preserving the other linear-autoscaler parameters (`coresPerReplica: 256`, `nodesPerReplica: 16`).
- Register the new manifest in the dev cluster overlay so ArgoCD's existing `core` Application reconciles it continuously (auto-recovering from any GKE-side resets, e.g., during cluster upgrades).
- Document this as the GCP-supported customization path: per `cloud.google.com/kubernetes-engine/docs/concepts/kube-dns`, editing the autoscaler ConfigMap IS the documented knob; the alternative "custom kube-dns Deployment" path is explicitly heavier and out of scope.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `gke-standard-infrastructure`: ADD a requirement constraining the dev cluster's `kube-dns-autoscaler` ConfigMap to `preventSinglePointFailure: false`, with verification scenarios for ConfigMap state and the resulting `kube-dns` Deployment replica count.

## Impact

- **Affected code**:
  - `cloud-provisioning/k8s/cluster/overlays/dev/kube-dns-autoscaler.yaml` (new) — the dev-only ConfigMap manifest
  - `cloud-provisioning/k8s/cluster/overlays/dev/kustomization.yaml` (edit) — register the new resource
  - `specification/openspec/specs/gke-standard-infrastructure/spec.md` (edit at archive time) — sync the new requirement
- **Affected systems**: dev GKE cluster `standard-cluster-osaka` only. No prod/staging changes; they retain GKE's default `preventSinglePointFailure: true`. No Pulumi changes.
- **Estimated savings**: ~¥1,300/month from retiring the 3rd spot node (e2-medium spot VM + 30 GB pd-standard boot disk + external IPv4). Combined with the previous change's ~¥3,800/month boot-disk savings, the dev Compute Engine SKU lands at ~¥4,400/month from the original ¥9,953/month — meeting the original ≥50% reduction target.
- **Deployment risk**: brief DNS lookup gaps when the single `kube-dns` pod is rescheduled (Spot preemption, node drain, rolling update). Browsers, Go HTTP clients, and the in-cluster `node-local-dns` cache retry transparently for the vast majority of lookups.
- **Dependencies**: none. ArgoCD's `core` Application (sync-wave: 1, path `k8s/cluster/overlays/dev`, automated sync + selfHeal) already covers the deploy path.
