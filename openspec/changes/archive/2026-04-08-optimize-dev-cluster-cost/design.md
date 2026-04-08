## Context

The dev GKE cluster recently migrated from Autopilot to Standard. After the migration, three unexpected cost drivers emerged:

1. **ADVANCED_DATAPATH (Dataplane V2 / eBPF)** is enabled on the cluster, deploying an `anetd` DaemonSet that consumes a fixed 195m CPU per node. This is a networking backend feature (NetworkPolicy enforcement, flow logging, multi-NIC) that provides zero value in a 2-node dev cluster with no NetworkPolicy resources.

2. **Google Managed Prometheus (GMP)** is enabled by default, deploying `gmp-system/collector` DaemonSet pods. All active alert policies are log-based (not metrics-based), so GMP contributes cost with zero benefit.

3. **CPU requests are calibrated for Autopilot Bursting** (50m minimum), which was the correct floor for Autopilot but unnecessarily inflates Cluster Autoscaler scheduling pressure on Standard clusters. Requests drive autoscaler decisions — inflated requests trigger a second node even when actual CPU usage could fit on one.

With the current `e2-standard-2` node (1930m allocatable CPU), the first node fills up due to DaemonSet overhead (anetd 195m + gke-metadata-server 100m + fluentbit 105m + kube-dns 270m + kube-proxy 50m ≈ 720m) plus user pod requests (~50m × 12 pods ≈ 600m), totaling ~1320m and forcing a second node for scheduling headroom.

After removing ADVANCED_DATAPATH and GMP and reducing requests to 10m: DaemonSet fixed cost drops to ~525m, user pod requests drop to ~120m, total ~645m per node — comfortably under e2-medium's 940m allocatable, enabling a single-node idle state.

## Goals / Non-Goals

**Goals:**
- Reduce dev cluster monthly Compute Engine cost by ~50% through machine type downsize and node count reduction
- Eliminate GMP DaemonSet cost (zero benefit in dev)
- Eliminate ADVANCED_DATAPATH overhead (zero benefit in dev)
- Right-size all dev pod CPU requests to reflect actual usage, reducing autoscaler trigger threshold
- Cap ScaledObject maxReplicaCount at 1 for consumer workloads in dev

**Non-Goals:**
- Changing prod or staging cluster configurations
- Removing monitoring coverage (log-based alerts remain fully functional)
- Modifying memory limits (already right-sized in a prior change)
- Optimizing the L7 External Load Balancer cost (fixed ~¥2,700/month, no optimization available)

## Decisions

### Decision 1: Disable ADVANCED_DATAPATH rather than tolerate its cost

**Choice:** Remove `datapathProvider: 'ADVANCED_DATAPATH'` from the dev cluster definition (defaulting to `LEGACY_DATAPATH`).

**Rationale:** ADVANCED_DATAPATH is designed for clusters that use Kubernetes NetworkPolicy enforcement, flow logging, multi-network interfaces, or FQDN-based policies. The dev cluster has zero NetworkPolicy resources, no NetworkLogging, and no multi-NIC setup. The `anetd` DaemonSet consumes 195m CPU per node with no return.

**Alternative considered:** Keep ADVANCED_DATAPATH and accept the cost (~¥3,000/month extra). Rejected because there is no security or networking capability the dev cluster needs from it.

**Constraint:** GKE does not support in-place datapath provider changes — cluster recreation is required. This is acceptable given a recent cluster recreation was already performed for the Autopilot→Standard migration.

### Decision 2: Explicitly disable GMP and restrict observability components

**Choice:** Add `monitoringConfig: { enableComponents: ['SYSTEM_COMPONENTS'], managedPrometheus: { enabled: false } }` and `loggingConfig: { enableComponents: ['SYSTEM_COMPONENTS'] }` to the dev cluster.

**Rationale:** Verified that all alert policies in `monitoring.ts` use `resource_type: k8s_container` with log-based filters (severity >= ERROR). None reference GMP metric descriptors. Disabling GMP removes DaemonSet collector pods from every node at zero operational impact.

**Alternative considered:** Disable GMP via GKE Console toggle only. Rejected — Pulumi manages cluster state; console changes would be reverted on next `pulumi up`. The change must be in code.

### Decision 3: Switch to e2-medium × max 2 nodes

**Choice:** Change machine type to `e2-medium` and `maxNodeCount: 2`.

**Rationale:** Post-optimization DaemonSet fixed cost per node is ~525m. With 10m requests per user pod and ~12 pods per node, total scheduled requests are ~645m, which fits within e2-medium's 940m allocatable CPU. A second node is still possible for burst bursts but the autoscaler will not trigger it at idle. Spot e2-medium saves ~50% compared to Spot e2-standard-2 on the CE line.

**Constraint:** e2-medium uses shared-core (burstable) CPU. The 2 vCPU is shared; the GKE-enforced allocatable ceiling is 940m. This is sufficient because all workloads in dev are latency-tolerant and lightly loaded.

**Alternative considered:** Keep e2-standard-2 but reduce to maxNodeCount 2. Rejected — the savings from the machine type change are significant and the feasibility analysis confirms e2-medium is sufficient after the DaemonSet reductions.

### Decision 4: Reduce CPU requests floor from 50m to 10m

**Choice:** Set all dev pod CPU requests to 10m (from 50m).

**Rationale:** The 50m floor was mandated by GKE Autopilot Bursting, which requires a minimum 50m CPU request per container. On Standard GKE, there is no such minimum. Actual CPU usage for idle backend/argocd/keda/nats pods is consistently below 5m. Setting 10m provides a small safety margin above observed usage while allowing the Cluster Autoscaler to defer scaling out.

**Exception:** `argocd-application-controller` retains a higher request (20m CPU, 320Mi memory) because it exhibits genuine periodic CPU spikes (reconciliation loops) and historically uses ~307Mi memory at rest.

**Alternative considered:** Keep 50m requests to give pods more scheduling headroom. Rejected — on Standard GKE, requests (not actual usage) drive autoscaler decisions, so lower requests reduce cost without reducing available CPU burst capacity.

### Decision 5: Set ScaledObject maxReplicaCount to 1 for consumer-app in dev

**Choice:** Patch consumer-app's ScaledObject to `maxReplicaCount: 1`.

**Rationale:** The consumer-app processes NATS messages. In dev, message volume is negligible. Horizontal scale-out provides no benefit and wastes resources. `minReplicaCount: 0` (zero-scale on idle) is preserved.

## Risks / Trade-offs

- **[Risk] Cluster recreation disruption** → The dev cluster must be destroyed and recreated to change `datapathProvider`. Mitigation: coordinate timing with the team; ArgoCD will automatically redeploy all workloads from GitOps manifests after cluster recreation. Estimated downtime: ~10–15 minutes.

- **[Risk] e2-medium CPU ceiling during CI or batch operations** → If multiple workloads spike simultaneously, the 940m ceiling could cause throttling. Mitigation: `maxNodeCount: 2` allows the autoscaler to add a second node if requests exceed first-node capacity. CPU limits (100m for most pods) prevent a single runaway pod from starving others.

- **[Risk] GMP disabled → loss of metric-based alerting potential** → Currently no alerts use GMP, but future engineers may add metric-based alerts unaware GMP is disabled. Mitigation: document in the spec that dev GMP is intentionally disabled; any metric alert must use log-based filtering instead, or GMP must be re-enabled.

- **[Risk] kube-dns replica count with 2-node cluster** → `kube-dns-autoscaler` uses `preventSinglePointFailure: true`, which forces 2 replicas when `nodes > 1`. With maxNodeCount 2, kube-dns will run 2 replicas when both nodes are present, consuming 540m CPU total. Mitigation: this is acceptable — kube-dns requests are 270m each, within budget with 2 nodes.

## Migration Plan

1. **Implement Kubernetes manifest changes** (no cluster disruption):
   - Right-size CPU requests in all dev overlays
   - Set ScaledObject maxReplicaCount to 1 for consumer-app
   - Add resource patches for system namespaces (argocd, keda, nats, otel-collector, external-secrets, atlas-operator, reloader)

2. **Implement Pulumi cluster changes** (`kubernetes.ts`):
   - Remove `datapathProvider: 'ADVANCED_DATAPATH'`
   - Add `loggingConfig` with `SYSTEM_COMPONENTS` only
   - Add `monitoringConfig` with GMP disabled
   - Change `machineType` to `e2-medium`
   - Change `maxNodeCount` to 2

3. **Open PR to cloud-provisioning** — CI runs `make lint` (biome + tsc + kustomize + kube-linter)

4. **Merge PR** — Pulumi Cloud Deployments automatically runs `pulumi up` for dev stack

5. **Cluster recreation** — Pulumi will detect datapath provider change and trigger node pool replacement or cluster recreation; confirm in `pulumi preview` output before merge

6. **Verify** — Confirm ArgoCD syncs all apps, pods reach Running state, and GKE node count stabilizes at 1 under idle load

**Rollback:** Revert the PR. Pulumi will restore previous configuration. Cluster recreation (back to e2-standard-2 + ADVANCED_DATAPATH) follows the same process.

## Open Questions

- Does Pulumi's GKE resource handle the datapath provider change via in-place update or full cluster replacement? Must verify via `pulumi preview --diff` before merging — if it shows a replacement, schedule during low-activity period.
