## Context

The prod GKE cluster `standard-cluster-osaka` was provisioned by the `provision-prod-gcp-resources` change (archived as `2026-05-13-provision-prod-gcp-resources`) as a Standard regional cluster. At that time, design.md D1 chose Standard over Autopilot to preserve dev parity and retain node-pool-level control (Spot e2-medium with custom disk type, kube-dns autoscaler override, GMP off, etc.).

In the interim, two facts have surfaced that change the optimal mode:

1. **Free tier math when dev is retired**: The `$74.40/month` GKE free tier credit is per-billing-account and applies to *zonal Standard or Autopilot* clusters only. Today the credit is fully consumed by dev (zonal Standard) and the regional Standard prod cluster pays the full `$72/month` management fee. The team plans to retire the dev cluster after prod is live with real workloads. At that point, prod becomes the only cluster, and the credit fully covers Autopilot's management fee → `$0/month` if prod is Autopilot, but stays at `$72/month` if prod is Standard regional (regional Standard is not eligible).
2. **GMP cost on Autopilot is real but controllable**: GKE Autopilot ≥ 1.25 cannot disable managed collection. The historical dev cluster (when it was Autopilot) racked up a few thousand yen per month of GMP charges. Per [official cost-controls docs](https://docs.cloud.google.com/stackdriver/docs/managed-prometheus/cost-controls), the cost is reducible to a small floor (`$5-15/month`) via metric-relabel `drop` rules at scrape time and extending the scrape interval to 60s (75% reduction from the default 15s). The reduction has to be done in cluster config since system-pod scrapes are GKE-managed; user-level PodMonitoring opt-in handles workload metrics.

Net: post-dev-retirement, Autopilot prod costs `$5-22/month` total vs Standard regional prod's `$77-84/month`. The break-even has flipped.

Prod has zero application workloads currently — only the cluster control plane is running. This is the unique window where the irreversible cluster-mode flip is safe to perform without disrupting user traffic.

## Goals / Non-Goals

**Goals:**

- Replace the prod GKE Standard regional cluster with an Autopilot regional cluster, reusing all surrounding GCP resources (KMS key, VPC subnet, secondary IP ranges, Cloud SQL, Cloud DNS zones, Certificate Manager certs, static IP, Secret Manager secrets, GCP Service Accounts).
- Preserve the `prod-environment-bootstrap` capability's irreversible decisions (regional topology, Dataplane V2, etcd CMEK via the existing KMS key, CIDR plan) — they remain set in the new Autopilot cluster.
- Bake in GMP cost controls (60s scrape interval + metric-relabel filter that drops everything outside an explicit allow-list) at cluster creation so the empirical GMP cost stays in the `$5-15/month` band rather than the unfiltered `$30-60/month`.
- Keep the migration zero-data-loss: prod has no Pods, Secrets, or PVs to evacuate. Cluster destroy + create is the simplest path.

**Non-Goals:**

- Authoring k8s manifests for the new cluster (ArgoCD bootstrap, per-namespace overlays). Still tracked in the follow-up `prod-k8s-manifests` change, which now has one extra item: ClusterPodMonitoring for GMP cost control.
- Migrating dev to Autopilot. Dev's optimization (Standard zonal + Spot + GMP off + 30 GB pd-standard boot disk) is unrelated and stays.
- Retiring the dev cluster. That happens later, by a separate decision/action when prod is live with real workloads. This change is *forward-compatible* with that retirement — the cost savings materialize when dev goes away, but the new prod cluster works correctly alongside dev during the overlap.
- Re-architecting the network: same VPC, same subnet, same CIDR plan, same Cloud DNS zones, same Certificate Manager certs, same static IP. Only the cluster resource itself changes.

## Decisions

### D1: Cluster mode flips from Standard regional to Autopilot regional

**Decision:** New cluster mode is **Autopilot** (still regional `asia-northeast2`).

**Why:**

- Free tier covers Autopilot's `$72/month` management fee fully when dev is retired.
- Autopilot is Google's recommended default for new production workloads.
- Liverty Music's workload profile (HPA-driven web apps, no privileged DaemonSets, no GPU/accelerator demand) is exactly the Autopilot sweet spot.
- Operational savings: no node pool sizing, no autoscaler tuning, no boot-disk decisions, no GKE version-upgrade orchestration.

**Alternatives:**

- **Keep Standard regional**: pays `$72/month` indefinitely. Was justified pre-`provision-prod-gcp-resources` based on dev parity, but the parity argument weakens when dev is going away.
- **Switch to Standard zonal**: would qualify for free tier but loses HA (single AZ outage = total prod downtime). Unacceptable for prod even pre-launch.
- **Hybrid (Standard cluster with per-workload Autopilot ComputeClasses)**: Sept 2025 GKE feature. Adds operational complexity without solving the management-fee issue (Standard regional management fee is the bulk of the cost). Rejected.

**Reversibility:** Still irreversible. Mode flip requires cluster recreation. This is the second-and-last mode flip we expect to perform.

### D2: Cluster mode flip via destroy-and-recreate (not parallel cutover)

**Decision:** Pulumi destroys `standard-cluster-osaka` and creates a fresh `autopilot-cluster-osaka` (or keeps the same name; see D3). The two do not coexist.

**Why:**

- Prod has zero workloads. There is nothing to evacuate.
- Parallel cutover would require live workloads, two clusters running simultaneously (`$144/month` in management fees during overlap), DNS-level traffic shifting, and an extra rollback complexity layer — all overkill when the cluster is idle.
- Destroy-and-recreate is cleaner: one Pulumi transaction, fully reversible if the create step fails (re-apply old config).

**Alternatives:**

- **Parallel cutover with blue-green DNS shift**: justified if prod had live users. Not the case today. Save the technique for the much larger `migrate-prod-to-{multi-region|next-cluster-mode}` change if/when prod ever has real users.

**Risk**: a destroy that succeeds but a create that fails leaves prod cluster-less. Mitigation: validate the new Pulumi config in `pulumi preview --stack prod` exhaustively before the apply window; have the rollback Pulumi commit ready to revert if needed.

### D3: Cluster resource keeps the same name `standard-cluster-osaka` (or rename?)

**Decision:** Rename to `autopilot-cluster-osaka` for clarity.

**Why:**

- The cluster name "standard-cluster-osaka" was meaningful when Standard mode was the differentiator from dev's earlier Autopilot. Now that the cluster *is* Autopilot, keeping "standard" in the name is actively misleading.
- Pulumi URN change is unavoidable anyway (cluster mode flip = new resource). So renaming is free.
- All references in `docs/` (PROD_BOOTSTRAP_DECISIONS.md, runbooks/prod-cluster-credentials.md) get updated in lock-step.

**Alternative:** Keep `standard-cluster-osaka` to minimize doc churn. Rejected — the misleading name is a long-term tax.

**Impact:** runbooks that say `gcloud container clusters get-credentials standard-cluster-osaka ...` need updating to `autopilot-cluster-osaka`. `kubectl` context name changes too. This is documented in the change's tasks.

### D4: KMS key (etcd CMEK) is reused, not recreated

**Decision:** The new Autopilot cluster's `databaseEncryption.keyName` points at the existing `projects/liverty-music-prod/locations/asia-northeast2/keyRings/gke-cluster/cryptoKeys/gke-etcd-encryption`.

**Why:**

- The KMS key is a Pulumi-managed resource with `protect: true`. Destroying and recreating it would be operationally risky.
- The existing key has zero etcd contents pointing at it (since the old cluster had no Secrets in etcd) — there is no live data to re-encrypt. The new cluster starts encrypting *its* etcd with the same key from the first Secret onward.
- The KMS service-agent IAM binding for the GKE control plane remains valid (same project, same service agent identity).

### D5: GMP cost-control config is part of the cluster cutover

**Decision:** A `ClusterPodMonitoring` resource that drops all metrics outside an explicit allow-list, with `interval: 60s`, is applied to the new cluster as part of the cutover — not deferred to the `prod-k8s-manifests` follow-up.

**Why:**

- If the new Autopilot cluster runs even briefly with default GMP scrape config (15s interval, no relabel filter), GMP samples start ingesting immediately at the unfiltered rate. The cost-control config has to be in place before the first scrape cycle.
- The ClusterPodMonitoring resource is a Kubernetes CR, so it must be applied via `kubectl` or via the cluster's bootstrap mechanism. Since ArgoCD bootstrap is in the `prod-k8s-manifests` follow-up, this change applies the ClusterPodMonitoring directly via `kubectl apply -f` post-cluster-create.
- Default allow-list (initial cut, revisable later): `kube_(node|deployment|pod|namespace)_.+` (kube-state-metrics core series) and `container_(cpu|memory)_.+` (cAdvisor essentials). Everything else dropped.
- Scrape interval extends from default 15s → 60s for a 75% sample-volume reduction per [Google's cost-optimization guidance](https://docs.cloud.google.com/stackdriver/docs/managed-prometheus/cost-controls).

**Alternative:** Defer to `prod-k8s-manifests`. Rejected because GMP starts billing the second the cluster's control plane is up; a deferred config means a billable window of unfiltered ingestion.

### D6: Spot pricing remains the default for Pods via the existing `gke-spot` label

**Decision:** Pods continue to request Spot scheduling via the existing `cloud.google.com/gke-spot: "true"` nodeSelector. Autopilot honors this and bills the Pod at Spot rates.

**Why:**

- The `gke-spot` label is already enforced in every dev pod template per the `gke-standard-infrastructure` spec. Workload manifests do not need to change between Standard and Autopilot.
- Spot Pod billing in Autopilot: approximately `$0.00475/vCPU/hr + $0.00053/GB/hr` (per the GCP pricing page), which is comparable to running Spot VMs on Standard and *cheaper than* running on-demand Pods on Autopilot.
- Once real users arrive and SLO concerns appear, on-demand Pods can be requested by removing the label — no cluster reconfig needed.

### D7: Static IP and DNS records are retargeted, not replaced

**Decision:** Re-bind the existing `api-gateway-static-ip` to the new Autopilot cluster's Gateway. Cloud DNS A records keep pointing at the same IP throughout. Certificate Manager certs are reused.

**Why:**

- DNS propagation delays are eliminated — no record changes.
- ACME challenge state is preserved — certs don't need re-issuance.
- The Gateway resource itself is a Kubernetes CR, applied to the new cluster via the same mechanism as the ClusterPodMonitoring (D5).
- Brief unbind window: between when the old cluster's Gateway is destroyed and the new cluster's Gateway claims the static IP. Acceptable since no live traffic.

## Risks / Trade-offs

- **[Risk] Destroy succeeds, create fails → prod is cluster-less.** → Mitigation: thorough `pulumi preview --stack prod` review before apply, plus a pre-staged rollback Pulumi config (one git commit ready to revert to the Standard regional definition). Worst case: `~15 minutes` of "no prod cluster" while rolling back, which is acceptable since no users yet.
- **[Risk] Autopilot Pod-billing model surprises at scale.** Once workloads land and Pod count grows, Autopilot's per-vCPU pricing may exceed Standard's per-VM pricing for densely-packed workloads. → Mitigation: monitor monthly bills after `prod-k8s-manifests` lands; document the crossover threshold in `PROD_BOOTSTRAP_DECISIONS.md` "Future Revisit Triggers". The break-even for Liverty Music workloads is around 50+ Pods; if the team approaches that scale, re-evaluate.
- **[Risk] GMP cost-control config has a bug, allows expensive metrics through.** → Mitigation: review the ClusterPodMonitoring `metricRelabeling` config before apply; check the GCP billing dashboard daily for the first week post-cutover.
- **[Risk] Autopilot's Spot Pod supply fluctuates in `asia-northeast2`.** → Mitigation: same risk as Standard's Spot e2-medium pool; mitigated the same way (Autopilot will fall back to on-demand if Spot is unavailable, at higher cost but with availability).
- **[Trade-off] We lose the ability to override system add-ons (kube-dns autoscaler, NodeLocal DNSCache, GMP scrape config at the GKE level).** → Acceptable: those overrides made sense on the cost-pressured 3-node dev cluster but are unnecessary at prod's expected scale.
- **[Trade-off] We lose the granular GMP off/on switch.** → Acceptable: dev keeps `managedPrometheus.enabled: false`; prod accepts GMP-with-filter. Different envs, different tradeoffs.

## Migration Plan

Single Pulumi commit, executed as one `pulumi up --stack prod` operation:

1. **Pre-flight (out of band)**:
   - Confirm prod cluster has no Secrets, Deployments, Services, or PVs that reference live data (`kubectl get all,secrets,pvc -A`). Expected: only `kube-system` defaults.
   - Confirm `verify-prod-spec-scenarios.sh` from the prior change still passes (47/47) — establishes a clean pre-migration baseline.
   - Snapshot the prod stack: `pulumi stack export --stack prod > pre-migrate-prod-state.json` so we can roll back to the exact pre-migration state if needed.

2. **Code change in `cloud-provisioning`** (one PR):
   - `src/gcp/components/kubernetes.ts`: prod branch's `gcp.container.Cluster` flips to `enableAutopilot: true`. The `spot-pool-osaka` `gcp.container.NodePool` block is removed. Resource name changes from `standard-cluster-osaka` → `autopilot-cluster-osaka`.
   - `src/gcp/components/kms.ts`: no change.
   - `src/gcp/components/network.ts`: no change.
   - `docs/PROD_BOOTSTRAP_DECISIONS.md` and `docs/runbooks/prod-cluster-credentials.md`: update cluster name references; add migration history note.

3. **Apply (Pulumi Cloud console)**:
   - Trigger `pulumi preview --stack prod` first (will run automatically as part of the PR's `liverty-music/prod - preview deployment`). Expected diff: `~10 to delete` (old cluster + node pool + cluster-attached IAM) and `~10 to create` (new Autopilot cluster + IAM rebindings). KMS / Cloud SQL / DNS resources stay unchanged.
   - Trigger `pulumi up --stack prod` manually after merge (per the existing `deployment-infrastructure` spec's "Manual Deployment Flow (Prod)" requirement).
   - Apply duration: ~15 minutes (Autopilot cluster creation takes a similar time to Standard regional creation).

4. **Post-create configuration (one-shot, via kubectl)**:
   - `gcloud container clusters get-credentials autopilot-cluster-osaka --region asia-northeast2 --project liverty-music-prod`.
   - `kubectl apply -f cluster-pod-monitoring.yaml` (the GMP cost-control config). The yaml is committed in `cloud-provisioning/k8s/cluster/overlays/prod/`. This is the *only* k8s manifest the migration introduces; everything else is deferred to `prod-k8s-manifests`.
   - Verify ingestion is filtered: query `monitoring.googleapis.com/api/v1/series` count after 5 minutes, confirm it's bounded.

5. **Verification**:
   - Re-run `verify-prod-spec-scenarios.sh` (will fail several scenarios on the spec wording since the spec is being updated; the post-migration spec scenarios are what passes now).
   - Confirm `gcloud container clusters describe autopilot-cluster-osaka --region asia-northeast2 --project liverty-music-prod --format='value(autopilot.enabled,databaseEncryption.state,networkConfig.datapathProvider)'` returns `True ALL_OBJECTS_ENCRYPTION_ENABLED ADVANCED_DATAPATH`.
   - Confirm GCP billing dashboard shows the management fee dropping in the next billing period.

6. **Rollback strategy**:
   - If create step fails: `pulumi stack import` from `pre-migrate-prod-state.json`, then re-apply the pre-migration code (one git revert commit).
   - If create succeeds but discovers problems within `<2 days`: same procedure, plus destroy the new Autopilot cluster to avoid double-management-fee billing.
   - Beyond 2 days: rollback gets harder (KMS key history, billing cycle, etc.). Treat the post-2-day state as a soft commit.

## Open Questions

- **OQ1: ClusterPodMonitoring allow-list scope.** The initial allow-list (`kube_(node|deployment|pod|namespace)_.+` plus `container_(cpu|memory)_.+`) is a minimal-cost cut. Future workloads (e.g., backend with custom Prometheus metrics) will need additions. Should we ship a `prod-k8s-manifests`-style mechanism for per-workload allow-list extension, or expand the cluster-wide allow-list ad hoc? *Default decision unless raised before implementation:* start minimal; extend per workload via opt-in PodMonitoring CRDs in the `prod-k8s-manifests` follow-up.
- **OQ2: Cluster name during migration.** Does renaming `standard-cluster-osaka` → `autopilot-cluster-osaka` add value, or is it just churn? *Default decision unless raised before implementation:* rename, per D3.
- **OQ3: Timing of dev retirement.** This change works whether dev is still running or already retired. But the *cost savings* only materialize after dev is gone (because dev currently consumes the free tier). Should we sequence this change with dev retirement explicitly? *Default decision unless raised before implementation:* perform this migration independently, and treat dev retirement as a separate concern. The new prod Autopilot cluster runs correctly during the dev-overlap period; only the cost benefit is dev-retirement-gated.
