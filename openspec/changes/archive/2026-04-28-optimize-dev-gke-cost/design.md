## Context

The dev Compute Engine bill jumped to ¥9,953/month (+1403%) following the Apr 8 Autopilot→Standard switch and the Apr 21 self-hosted Zitadel deployment. Two specific configurations dominate the spend:

1. **Boot disks**: 3 nodes × 100GB pd-balanced = ~¥4,500/month. The 100GB size is the GKE NodePool default when `diskSizeGb` is unspecified; pd-balanced is the default `diskType`. Neither is justified for dev — image cache and OS rarely exceed 10GB.
2. **3rd Spot node**: forced by Zitadel API+Login Deployments running 2 replicas each with `requiredDuringSchedulingIgnoredDuringExecution` pod anti-affinity. With 4 replicas and `topologyKey: kubernetes.io/hostname`, the scheduler cannot pack onto 2 nodes, so the autoscaler permanently runs at the new `maxNodeCount: 3`.

The cluster currently runs at ~85% CPU request packing across 3 e2-medium nodes (940m allocatable each). Removing one Zitadel API replica (120m total, including its cloud-sql-proxy and bootstrap-uploader sidecars) plus one Login replica (50m) frees enough headroom that the autoscaler can downscale to 2 nodes when load is idle, eliminating the 3rd node's compute, disk, and external IP charges.

dev does not require HA: a Spot preemption already causes 1-2 minute service interruptions even with 2 replicas. The cost-vs-availability trade-off favors aggressive cost reduction.

## Goals / Non-Goals

**Goals:**
- Lower dev Compute Engine SKU spend by ≥50% (target ~¥4,400/month).
- Use the cheapest disk type compatible with the existing E2 machine series.
- Keep the change reversible: each modification is a single config flip, not a topology change.
- Preserve the Standard cluster + Spot nodes + public IP architecture chosen on Apr 8 (no Cloud NAT regression).

**Non-Goals:**
- Migrating to a different machine series (e.g., N4 with Hyperdisk Throughput). E2 remains the cheapest GCP general-purpose family for the dev workload size.
- Touching staging or prod overlays. This change is dev-only.
- Refactoring the Zitadel base manifest. Replicas are tuned via overlay only, preserving multi-environment defaults.
- Removing the 3rd-node capacity headroom. `maxNodeCount: 3` is retained as autoscaler ceiling; only the *forced* 3rd-node baseline is eliminated.
- Removing the cloud-sql-proxy Deployment added Apr 13 for local DB access. That tool is operator-facing infrastructure; removing it is a separate scope.

## Decisions

### Decision 1: pd-standard 30GB for Spot pool boot disk

**Choice:** `diskType: pd-standard`, `diskSizeGb: 30`.

**Why:**
- E2 machine series does NOT support any Hyperdisk variant per `cloud.google.com/compute/docs/disks/hyperdisks` (Balanced, Throughput, Extreme, ML all show `—` for E2). Hyperdisk Throughput would otherwise be the cheapest at small sizes for newer series.
- Among E2-compatible types (pd-standard / pd-balanced / pd-ssd), pd-standard is the cheapest at $0.052/GB/month in asia-northeast2 (vs $0.10 for pd-balanced, $0.17 for pd-ssd).
- 30GB is GKE's recommended minimum. 10GB and 20GB options were considered but rejected: GKE evicts pods at 85% disk full (`DiskPressure` taint), and Container-Optimized OS plus the cluster's typical image cache (zitadel + cloud-sql-proxy + backend + frontend + ArgoCD + KEDA + Atlas + ESO + Reloader + OTel images) routinely consumes 8-12GB. 20GB tightens but works; 10GB risks frequent image GC churn and surprise evictions.
- pd-standard is HDD-backed with low IOPS, which slows cold node bootstrap and image pull by a few seconds — acceptable for dev where node churn is rare.

**Alternatives considered:**
- `pd-balanced 30GB` — would still save ~¥3,150/month vs current 100GB pd-balanced, but pd-standard saves additional ~¥650/month for no functional cost in dev.
- `pd-standard 20GB` — saves an extra ~¥230/month vs 30GB. Marginal benefit, higher risk of hitting `DiskPressure` during multi-image pulls. Rejected.
- Switch to N4 + Hyperdisk Throughput — N4 base price exceeds E2 by enough that net cost rises. Rejected.

### Decision 2: Zitadel dev replicas → 1 (both API and Login)

**Choice:** Patch dev overlays for both `zitadel` and `zitadel-login` Deployments to `replicas: 1`.

**Why:**
- A single replica eliminates the `podAntiAffinity: required` constraint's effect (no siblings to spread). The autoscaler can then pack the cluster onto 2 nodes when idle.
- Zitadel API replica savings: 1 × (zitadel 100m + cloud-sql-proxy 10m + bootstrap-uploader 10m) = 120m CPU, 352Mi memory, plus boot disk image cache pressure.
- Zitadel Login replica savings: 1 × 50m CPU, 128Mi memory.
- Spot preemption already causes brief outages with 2 replicas (a single Spot zone preemption can take both replicas if landed on adjacent nodes despite anti-affinity, since anti-affinity is hostname-scoped and Spot preemption is zone-scoped). Dropping to 1 replica converts the failure mode from "rare both-replica preemption" to "any preemption causes ~90s outage" — material in prod, immaterial in dev.

**Alternatives considered:**
- Keep `replicas: 2`, change anti-affinity from `required` → `preferred` — would let the scheduler pack both replicas onto one node when needed, achieving similar autoscaler outcomes. Rejected because it doubles CPU/memory/disk overhead vs single replica with no dev-visible benefit.
- Set `replicas: 0` and use Zitadel Cloud — undoes the Apr 21 self-hosted migration entirely. Out of scope; that migration was completed for reasons unrelated to cost.

### Decision 3: PDB `minAvailable: 0` in dev overlay

**Choice:** Add `pdb-patch.yaml` to the dev overlay, patching both `zitadel` and `zitadel-login` PDBs to `minAvailable: 0`.

**Why:**
- The base PDB declares `minAvailable: 1`. With `replicas: 1`, the only pod is also the only voluntarily-evictable pod, and `minAvailable: 1` blocks eviction permanently. This breaks `kubectl drain`, ArgoCD-driven rollouts, GKE node auto-upgrade, and graceful Spot preemption.
- `minAvailable: 0` allows voluntary disruption while preserving the PDB resource (so prod/staging continue to enforce `minAvailable: 1` from the base).
- Alternative `kubectl delete pdb` via overlay's `patches: [{op: remove}]` was considered but rejected — keeping the resource present and merely relaxed makes prod/staging vs dev diff cleaner.

### Decision 4: Retain `maxNodeCount: 3`

**Choice:** Do not lower the autoscaler ceiling.

**Why:**
- Lowering to 2 risks `Pending` pods if cluster load briefly spikes (e.g., during a NodePool replace, batch job runs concert-discovery, or rolling deploys overlap). The autoscaler bills only for *running* nodes — keeping the ceiling at 3 is free insurance.
- After this change, expected steady-state is 2 nodes; 3rd node only spins up under transient load and downscales after the autoscaler's idle threshold (~10 minutes).

## Risks / Trade-offs

- **NodePool boot disk reconfiguration is in-place (verified via `pulumi preview`)** → `diskSizeGb` and `diskType` changes resolve to `~ update` on the existing `spot-pool-osaka` NodePool, with 206 other resources untouched. GKE rolls out the new disk template via surge upgrade (node-by-node), respecting PDBs. With dev PDBs relaxed to `minAvailable: 0`, the single Zitadel/backend/frontend replica drains cleanly and reschedules onto the next node. Expected user-visible downtime per pod: <90 s during its single eviction window.
- **30GB pd-standard slower bootstrap** → New nodes take ~30-60s longer to become Ready due to HDD image pull. Acceptable for dev. Mitigation: none needed; not user-facing.
- **`replicas: 1` Zitadel = single point of failure during deploys** → Rolling deploy briefly has zero pods (maxUnavailable=0 + maxSurge=1 means new pod starts before old terminates, so brief overlap is preserved). Worst case: ~30s gap if new pod fails readiness. Mitigation: rely on browser retry; dev users can refresh.
- **Autoscaler may not downscale to 2** → If the post-change CPU request total still exceeds 1880m (2 × 940m), 3rd node stays up and savings are partial. Mitigation: post-deploy verification step in tasks confirms node count and computes actual savings. If 3rd node persists, a follow-up change can right-size other workloads (cloud-sql-proxy Deployment, KEDA operator, OTel collector).
- **PDB relaxation in dev only** → No risk to prod since base PDB and prod overlay (no patch) keep `minAvailable: 1`. Verified by `kubectl kustomize k8s/namespaces/zitadel/overlays/dev` showing only the dev manifest is affected.

## Migration Plan

1. Pulumi changes deploy via the auto-`pulumi up` job triggered by merge to `main` (per cloud-provisioning CLAUDE.md). The NodePool in-place update happens inside that run; GKE then performs a surge upgrade across the spot pool's nodes.
2. Kustomize overlay changes apply via ArgoCD's existing sync to the `zitadel` Application after merge.
3. Verification (post-deploy):
   - `gcloud compute disks list` — boot disks show `30 pd-standard`.
   - `kubectl get nodes` — 2 or 3 nodes (down from current 3).
   - `kubectl get deploy -n zitadel` — both Deployments show `1/1` ready.
   - `kubectl get pdb -n zitadel` — both PDBs show `minAvailable: 0` for dev.
   - `gcloud billing` cost report after 7 days — Compute Engine SKU trends down to target ¥4,400/month range.

**Rollback:** revert the PR and re-deploy. NodePool reverts to 100GB pd-balanced via in-place update + surge upgrade; Zitadel replicas return to 2. No data migration concerns since boot disks are stateless and PVCs are untouched.
