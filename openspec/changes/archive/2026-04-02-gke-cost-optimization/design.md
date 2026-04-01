## Context

The dev environment runs on a GKE Autopilot cluster (`cluster-osaka`, `asia-northeast2`) with private nodes behind a Cloud NAT gateway. Autopilot's $0.10/hr management fee and Cloud NAT's $0.045/hr gateway fee are fixed costs independent of actual workload — they accrue 24/7 regardless of utilization. Together they represent ~¥16,000/month that can be eliminated.

The cluster hosts ~20 pods across 10 namespaces: ArgoCD, KEDA, NATS, External Secrets Operator, Atlas Operator, OTel Collector, Reloader, backend server, frontend, and their supporting pods. All workloads currently use `cloud.google.com/compute-class: autopilot-spot` nodeSelector.

Cloud SQL is accessed via Private Service Connect (PSC) at a static internal IP (10.10.10.10) — this is independent of whether nodes are private or public. All other GCP services (Secret Manager, Artifact Registry, Vertex AI) are accessible via public Google API endpoints with IAM auth.

## Goals / Non-Goals

**Goals:**
- Eliminate Autopilot cluster management fee (¥10,800/month)
- Eliminate Cloud NAT fixed costs (¥5,292/month)
- Maintain all existing workload functionality
- Keep Spot VM cost savings

**Non-Goals:**
- Staging or production changes
- Private Google Access optimization (separate change)
- Cloud Monitoring cost reduction
- Vertex AI cost optimization

## Decisions

### Decision 1: New cluster vs. in-place conversion

**Chosen: New cluster creation**

GKE does not support in-place Autopilot → Standard conversion. The migration requires creating a new Standard cluster, migrating workloads, then deleting the Autopilot cluster. Dev downtime is acceptable, so this is straightforward.

### Decision 2: Machine type for Standard node pool

**Chosen: `e2-standard-2` (2 vCPU, 8 GiB)**

Current workloads total ~2 vCPU / ~4 GiB requests across all pods including system pods. `e2-standard-2` provides headroom for kube-system overhead while remaining the smallest Standard machine that fits all workloads. At Spot pricing (~$0.027/hr), 2 nodes cost ~¥5,800/month — comparable to Autopilot Spot compute cost.

Alternatives considered:
- `e2-medium` (2 vCPU, 4 GiB): Too small; kube-system + ArgoCD alone exceeds 4 GiB
- `e2-standard-4` (4 vCPU, 16 GiB): Oversized and unnecessarily expensive

### Decision 3: Public nodes (eliminate Cloud NAT)

**Chosen: `enablePrivateNodes: false`**

With public nodes, each node gets an external IP and can reach the internet directly — eliminating the Cloud NAT gateway. Security implications for dev are acceptable:
- GKE automatically manages firewall rules; nodes are not directly accessible from the internet on application ports
- No `masterAuthorizedNetworks` is currently configured, meaning the control plane is already world-accessible; public nodes add no meaningful incremental risk
- No NodePort services exist; all services are ClusterIP
- Cloud SQL PSC uses an internal IP (10.10.10.10) and is unaffected by node visibility

The Cloud Router and Cloud NAT Pulumi resources are deleted for dev. The `enableDynamicPortAllocation` and related NAT config in `network.ts` are removed.

### Decision 4: nodeSelector label migration

**Chosen: Replace `cloud.google.com/compute-class: autopilot-spot` with `cloud.google.com/gke-spot: "true"`**

Autopilot uses a custom compute class label for spot scheduling. Standard clusters use the standard GKE Spot label. All `spot-nodeselector-patch.yaml` files in dev overlays must be updated. The change is mechanical and affects all namespaces uniformly.

### Decision 5: ArgoCD cluster registration

ArgoCD's in-cluster configuration (`argocd.argoproj.io/secret-type: cluster`) references the Kubernetes API server endpoint. After cluster recreation, the endpoint changes. Since ArgoCD is deployed to the same cluster it manages (in-cluster mode), no external cluster secret needs updating — ArgoCD uses the in-cluster service account automatically.

## Risks / Trade-offs

- **Spot VM eviction** → Autopilot handled eviction transparently; Standard requires workloads to tolerate node eviction. All existing deployments have `restartPolicy: Always` and KEDA handles consumer scaling. Risk is low.
- **Node pool sizing** → Auto-scaling (min:1, max:4) handles burst. If all pods are scheduled on 1 node and it gets evicted, brief downtime occurs before a new node provisions. Acceptable for dev.
- **kube-system overhead** → Standard clusters run more system daemonsets than Autopilot on each node. The `e2-standard-2` (8 GiB) provides sufficient headroom.
- **Public node IP churn** → Node external IPs are ephemeral. If any external service whitelists node IPs, that whitelist breaks on node replacement. No such whitelisting exists currently.
- **Shielded GKE Nodes** → GKE Autopilot enforces Shielded GKE Nodes (Secure Boot + Integrity Monitoring) automatically. Standard clusters do not — `shieldedInstanceConfig` must be set explicitly in the node pool config. This is especially important for public nodes (`enablePrivateNodes: false`).

## Migration Plan

**Note on cluster replacement:** The Pulumi resource name `cluster-${regionName}` is reused for the new Standard cluster. Pulumi detects a type change (Autopilot → Standard) and performs a `replace` operation — it destroys the existing Autopilot cluster and creates the new Standard cluster in one atomic step. There is no "old cluster remains running" window. Dev downtime during the Pulumi operation is expected and acceptable.

1. Run `pulumi preview` to confirm the plan: Standard cluster create + Autopilot destroy + NAT/Router delete
2. Run `pulumi up` (dev downtime begins)
3. Update kubeconfig to point to new cluster endpoint
4. ArgoCD syncs all applications automatically (GitOps — no manual kubectl apply needed)
5. Verify all pods are Running in new cluster
6. Verify nodes have external IPs (`kubectl get nodes -o wide`)

Rollback: If the new cluster fails to come up, revert the Pulumi code change and run `pulumi up` again to restore the Autopilot cluster. No partial state to clean up since it's a single replace operation.

## Open Questions

- None. Migration path is well-defined and dev downtime is accepted.
