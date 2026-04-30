## Context

The dev GKE cluster runs `kube-dns` as 2 replicas because the GKE-managed `kube-dns-autoscaler` ConfigMap ships with `preventSinglePointFailure: true`. The autoscaler is the upstream Kubernetes `cluster-proportional-autoscaler` (kubernetes-sigs/cluster-proportional-autoscaler); its decision logic for our cluster is:

```
replicas = max(
  ceil(total_cores / coresPerReplica),    = ceil(6 / 256)  = 1
  ceil(total_nodes / nodesPerReplica),    = ceil(3 / 16)   = 1
  min,                                     = 1
)
# preventSinglePointFailure: true forces ≥2 if total_nodes ≥ 2
```

The single-point-of-failure guard is the only reason kube-dns sits at 2 replicas. Each pod requests 270m CPU, so 2 replicas consume 540m — by far the largest non-DaemonSet CPU draw in the cluster (next is Zitadel API at 120m). With ~270m freed (one of the two replicas removed), the cluster's total request budget drops to ~2018m. Although that still exceeds the 2-node allocatable ceiling (1880m) on raw request math, the cluster autoscaler scales on per-node utilization rather than aggregate requests, and retiring a node also removes that node's per-node DaemonSet pods (~378m worth). The actual post-compaction state recorded in tasks.md is ~1614m on 1880m capacity (86% packed, ~266m headroom).

GKE's stance on customization (verified across two official pages):

- **`cloud.google.com/kubernetes-engine/docs/concepts/kube-dns`** ("About kube-dns for GKE") explicitly documents the ConfigMap as the supported tuning knob: *"You can modify the number of `kube-dns` replicas by editing the `kube-dns-autoscaler` ConfigMap."* The four mentioned fields are `coresPerReplica`, `nodesPerReplica`, `min`, `max`, and `preventSinglePointFailure`.
- **`cloud.google.com/kubernetes-engine/docs/how-to/custom-kube-dns`** ("Set up a custom kube-dns Deployment") describes the heavier alternative — scaling the GKE-managed `kube-dns` and `kube-dns-autoscaler` Deployments to 0 and shipping a self-maintained replacement. That path explicitly transfers ongoing maintenance ownership and is overkill for a single-flag change.

## Goals / Non-Goals

**Goals:**
- Free ~270m CPU by reducing `kube-dns` to 1 replica in dev, enough headroom for the cluster autoscaler to retire the 3rd spot node.
- Use the GCP-documented light-touch path (ConfigMap edit) rather than the heavyweight custom-Deployment path.
- Make the configuration drift-resistant: ArgoCD reconciles continuously, so any GKE-side reset (cluster upgrade, auto-repair) is corrected within minutes.
- Keep the change strictly dev-scoped via Kustomize overlay; prod and staging continue inheriting GKE's `preventSinglePointFailure: true` default.

**Non-Goals:**
- NOT switching to NodeLocal DNSCache or any other DNS topology change. The cache already runs as a DaemonSet (existing).
- NOT replacing the GKE-managed `kube-dns` with a custom Deployment.
- NOT modifying `coresPerReplica`, `nodesPerReplica`, `min`, or `max`. Only the single boolean.
- NOT lowering the spot pool's `maxNodeCount` to force compaction. The autoscaler will downscale on its own once the CPU pressure clears.
- NOT awaiting or short-circuiting the 2026-05-04 scheduled cost-verification agent. That agent verifies the *combined* result of `optimize-dev-gke-cost` plus this change.

## Decisions

### Decision 1: ConfigMap override via dev overlay (vs Pulumi)

**Choice:** Add the ConfigMap manifest under `k8s/cluster/overlays/dev/` and register it in the dev kustomization. ArgoCD's existing `core` Application (path `k8s/cluster/overlays/dev`, sync-wave 1, automated sync + selfHeal) reconciles it.

**Why:**
- The cluster-level overlay is already where dev-only kube-system overrides belong (it currently hosts the dev `ClusterSecretStore` patch). Adding a sibling ConfigMap is symmetric.
- ArgoCD `selfHeal: true` is the strongest available drift-recovery story: any GKE-side reset is corrected within the sync interval, no human intervention.
- Dev-only by virtue of overlay placement — prod/staging cannot accidentally inherit it.

**Alternatives considered:**
- Manage via Pulumi `gcp.k8s.core.v1.ConfigMap` — Pulumi is meant for GCP-side primitives in this project, not in-cluster manifests. Mixing them would muddy the source-of-truth split (Pulumi for GCP, ArgoCD/Kustomize for k8s). Rejected.
- One-shot `kubectl edit` — works once, but offers no drift recovery and no audit trail. Rejected.
- Patch the existing kube-dns-autoscaler ConfigMap in-place via Kustomize JSON6902 patch — equivalent functionally, but the upstream ConfigMap's `data.linear` field is a JSON-serialized string (not a structured field), so a strategic merge or full-replacement manifest is cleaner than a patch. Rejected in favor of full-replacement.

### Decision 2: Provide a full ConfigMap (not a patch)

**Choice:** The dev overlay provides the entire `kube-dns-autoscaler` ConfigMap as a resource (with all fields explicit), not a partial patch.

**Why:**
- The upstream cluster-proportional-autoscaler reads `data.linear` as a single JSON string. A field-level patch on this nested string is awkward (Kustomize doesn't natively edit JSON-in-string values).
- A complete ConfigMap manifest documents the dev-intended values as one readable block. Anyone reviewing the overlay sees the full configuration, not just the diff.
- ArgoCD treats this as a regular Apply: kubectl server-side-apply merges fields, overwriting any GKE-default values for fields we declare. The `data.linear` JSON gets fully replaced with our string.

**Alternatives considered:**
- Strategic merge patch on `data.linear` — Kustomize cannot parse JSON-in-string fields. Rejected.
- JSON6902 patch with full-string replacement — works but obscures readability. Rejected.

### Decision 3: Preserve `coresPerReplica`, `nodesPerReplica`, `min`, `max` at GKE defaults

**Choice:** The dev ConfigMap keeps `coresPerReplica: 256, nodesPerReplica: 16` (and any default `min`, `max`), changing only `preventSinglePointFailure: true → false`.

**Why:**
- The autoscaler formula already correctly computes 1 replica for our cluster size. Changing other fields adds variables to the rollback story without benefit.
- Lower `coresPerReplica` (e.g., 128) would *increase* replicas as the cluster grows, the opposite of what we want.
- Tightening `max` would forbid scale-up if the dev cluster ever needs more DNS capacity (rare but possible during traffic spikes).

**Alternatives considered:**
- Set `min: 1, max: 1` to lock the replica count — works but is more aggressive than needed and removes the autoscaler's ability to scale up if dev workload grows. Rejected.

## Risks / Trade-offs

- **Single kube-dns replica = brief DNS gaps during pod reschedule** → Mitigation: the cluster's `node-local-dns` DaemonSet caches resolves locally on each node, masking most pod-reschedule gaps. Go HTTP clients and browsers retry transparently. Material risk only for ultra-latency-sensitive workloads, of which dev has none.
- **GKE may reset the ConfigMap during cluster upgrades** → ArgoCD's `selfHeal: true` reconciles within seconds, so the window of GKE-default behavior is short. Documented in design.md as expected behavior.
- **Future GKE policy could lock the ConfigMap** → If GKE starts treating the ConfigMap as managed (similar to the kube-dns Deployment itself), the override would stop working. Mitigation: when that happens, fall back to the documented "custom kube-dns Deployment" path. Probability low; not a blocker.
- **Estimated ¥1,300/month savings is conditional on autoscaler downscale** → If other workloads grow CPU requests in the meantime, the autoscaler may keep 3 nodes anyway. Mitigation: post-deploy verification step (re-check `kubectl get nodes` count) included in tasks.

## Migration Plan

1. PR opened against `cloud-provisioning/main`. CI green required.
2. On merge, ArgoCD's `core` Application picks up the new resource within one sync interval (~3 min).
3. ArgoCD applies the ConfigMap; the running `kube-dns-autoscaler` controller reads it on its next loop (~10 s) and scales `kube-dns` Deployment from 2 → 1.
4. Cluster autoscaler observes the freed 270m + idle headroom on the 3rd node. After the autoscaler's idle threshold (~10 min), the 3rd node is drained (PDBs respected) and removed.
5. Verification: `kubectl get deploy kube-dns -n kube-system` shows `1/1`; `kubectl get nodes -l cloud.google.com/gke-spot=true` shows 2 nodes.

**Rollback:** revert the PR. ArgoCD removes the dev ConfigMap on next sync; GKE's reconciler restores its default `preventSinglePointFailure: true`; kube-dns scales back to 2; autoscaler may add the 3rd node back if other workloads request it.
