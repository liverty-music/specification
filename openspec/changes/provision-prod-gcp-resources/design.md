## Context

The `liverty-music-prod` GCP project currently has only a `gcp:project` config and no Pulumi-managed resources. The Pulumi code in `cloud-provisioning/src/gcp/components/kubernetes.ts:384` and `network.ts:194` both `return` early when `environment === 'prod'`, leaving the prod stack as a deliberate no-op since 2026-02-05 (commit [`85fef89`](https://github.com/liverty-music/cloud-provisioning/commit/85fef89) "remove prod resources and optimize cloud sql dns").

The dev cluster's evolution over February-April 2026 — Autopilot regional → Standard zonal migration ([`05893f6`](https://github.com/liverty-music/cloud-provisioning/commit/05893f6) 2026-04-01), aggressive cost-optimization rounds ([`c0eae10`](https://github.com/liverty-music/cloud-provisioning/commit/c0eae10), [`943e6ef`](https://github.com/liverty-music/cloud-provisioning/commit/943e6ef)) — has produced a battle-tested set of decisions about which cluster settings matter and which can be deferred. This change leverages that learning to set up prod with the right irreversible decisions baked in from day 1, while keeping all reversible cost-deferrable settings at their cheapest values.

Two reference documents in the cloud-provisioning repo capture the underlying rationale and serve as operational context:
- `cloud-provisioning/docs/PROD_BOOTSTRAP_DECISIONS.md` — itemized decision log with reversibility classification.
- `cloud-provisioning/docs/GKE_CLUSTER_MODE_DECISION.md` — Autopilot-vs-Standard analysis and irreversibility reference table.

## Goals / Non-Goals

**Goals:**

- Provision prod GCP infrastructure that mirrors dev's workload set, so deployment manifests and Pulumi components can rely on prod having "the same shape" as dev.
- Bake in irreversible cluster settings (Dataplane V2, etcd CMEK, regional, ipAllocationPolicy) at creation time so they do not require a future cluster rebuild.
- Keep first-month cost under ¥25,000 by deferring every cost driver that is safely reversible (private nodes, Cloud NAT, GMP, on-demand nodes, boot disk CMEK, Confidential Nodes, HSM keys).
- Establish the prod Cloud KMS keyring + key needed for etcd CMEK as part of cluster creation, with correct IAM bindings for the GKE service agent.
- Preserve the existing dev cluster's behavior — this change is additive, not a refactor.

**Non-Goals:**

- Migrating any user data. Prod is empty; there is nothing to migrate from anywhere.
- Multi-region disaster recovery (single regional cluster in `asia-northeast2` only).
- Production-grade SLO monitoring (GMP stays off; deferred to "first users arrive" trigger).
- Blockchain key infrastructure (KMS asymmetric signing, Confidential signing node pool). Deferred to blockchain mainnet phase.
- Migrating prod to Autopilot. The mode choice is recorded as Standard; revisiting requires a new OpenSpec change since it implies cluster rebuild.
- Enforcement of network policies, pod security admission, or other Kubernetes-level hardening. Those are separate capability concerns.

## Decisions

### D1: Cluster mode is Standard (not Autopilot)

**Decision:** Use GKE Standard for prod, matching dev.

**Why:** The dev team has gained operational competence with Standard mode through the April optimization work. Standard provides the node-pool-level controls (Spot, machine type, disk type, autoscaler tuning) that have already produced concrete cost wins in dev. Same mental model across envs reduces ops friction.

**Alternatives considered:**
- **Autopilot regional**: Google's official "use for most production workloads" recommendation. Less operational toil. *Rejected for now* because (a) cluster mode is irreversible and we want to defer the decision until prod has real workload profile data, (b) the team's current playbook is Standard-centric, (c) Sept-2025 hybrid features (per-workload Autopilot ComputeClasses on Standard clusters) provide an escape hatch if we later want Autopilot semantics for specific workloads.

**Reversibility:** Irreversible (cluster mode cannot be flipped in-place; switch requires new cluster + workload migration).

### D2: Topology is regional (not zonal)

**Decision:** `location: asia-northeast2` (3-zone regional Standard cluster).

**Why:** Even without an SLO commitment, an AZ outage on a zonal cluster causes total prod downtime requiring manual intervention. Regional is the only sensible choice for prod, even pre-launch.

**Cost impact:** Regional Standard does NOT qualify for the GKE free tier (free tier covers Autopilot or zonal Standard only). Net additional cost: $0.10/hr × 720 hr ≈ $72/month (~¥10,800).

**Reversibility:** Irreversible.

### D3: Dataplane V2 enabled

**Decision:** Set `datapathProvider: 'ADVANCED_DATAPATH'` on the prod cluster.

**Why:**
- GCP has announced that Dataplane V2 becomes the default for new clusters on 2027-03-30 (per the GCP email received 2026-05). Enabling now aligns with the future default.
- NetworkPolicy enforcement is always-on with Dataplane V2 — a useful security baseline even though we are not authoring NetworkPolicy resources yet.
- eBPF-based dataplane has perf advantages for prod traffic volumes.
- Built-in network policy logging is valuable for future audit work.

**Alternatives considered:**
- **LEGACY_DATAPATH (current dev choice)**: Lower overhead on tiny clusters (no `anetd` DaemonSet). *Rejected for prod* because (a) prod will not stay tiny, (b) Dataplane V2 is irreversible — better to set it correctly at creation than face a re-create later, (c) Google is making this the default in 2027 regardless.

**Reversibility:** Irreversible. `--enable-dataplane-v2` cannot be applied to an existing cluster per [GKE docs](https://cloud.google.com/kubernetes-engine/docs/concepts/dataplane-v2): *"GKE Dataplane V2 can only be enabled when creating a new cluster."*

### D4: etcd CMEK enabled at cluster creation

**Decision:** Provision a Cloud KMS keyring and key in the prod project and configure the cluster's `databaseEncryption` to encrypt Kubernetes Secret resources using that key.

**Why:**
- Future SOC2 / blockchain security audit will almost certainly require encryption-at-rest with customer-controlled keys for Kubernetes Secret resources.
- Enabling after the fact is operationally fraught (cluster-wide re-encryption operation, IAM coordination).
- Cost is negligible: $0.06 / key version / month for software-backed keys, plus $0.03 / 10k operations. Free tier covers the first 20k operations/month per project. Estimated total: ~$0.20/month.

**KMS resource layout:**
- KeyRing name: `gke-cluster`, location: `asia-northeast2`.
- CryptoKey name: `gke-etcd-encryption`, purpose: `ENCRYPT_DECRYPT`, protection level: `SOFTWARE`, rotation period: 90 days (Cloud KMS handles rotation transparently).
- IAM binding: GKE service agent (`service-<project-number>@container-engine-robot.iam.gserviceaccount.com`) granted `roles/cloudkms.cryptoKeyEncrypterDecrypter` on the key.

**Alternatives considered:**
- **Cloud HSM-backed key** ($1 / key version / month): FIPS 140-2 Level 3 hardware HSM. *Deferred* — only needed if SOC2 auditor explicitly requires hardware key protection. Software key is upgradeable to HSM via key rotation if requirements tighten.
- **No CMEK** (use Google-managed encryption): default behavior. *Rejected* because enabling later requires cluster reconfiguration and lacks the audit-trail benefits of Cloud KMS.

**Reversibility:** Irreversible at cluster creation. Key rotation is supported (Cloud KMS) but flipping CMEK off after enabling is not a documented operation.

### D5: CIDR plan matches dev (project isolation handles conflict)

**Decision:** Reuse `NetworkConfig.Osaka` constants (`subnetCidr: '10.10.0.0/20'`, `podsCidr: '10.20.0.0/16'`, `servicesCidr: '10.30.0.0/20'`, `masterCidr: '172.16.0.0/28'`) for prod without modification.

**Why:**
- Environments are GCP-project-separated. VPCs are project-scoped; CIDR overlap between dev and prod VPCs is irrelevant unless we ever peer them, which is not in scope.
- Mental model is simplified by having one CIDR plan, not two.
- Current sizing comfortably supports prod at multi-year scale: Pod range `/16` = 65,536 IPs = ~256 nodes max (default `/24` per node); Service range `/20` = 4,096 services. Liverty Music prod is expected to operate well below those limits for the foreseeable future.

**Irreversibility focus:** Per [GKE alias-IPs docs](https://cloud.google.com/kubernetes-engine/docs/concepts/alias-ips), the **Service secondary range cannot be expanded or changed** after cluster creation. `/20` for services is generous and accepted as final. The Pod range can be expanded by adding additional Pod IP ranges (discontiguous CIDR) if scale ever exceeds 256 nodes — so under-sizing is recoverable.

**Alternatives considered:**
- **GKE-managed Services range** (`34.118.224.0/20`): default for new Standard clusters at GKE 1.29+. Frees up user VPC IP space. *Rejected for now* because using the same explicit CIDR plan as dev reduces IaC code divergence and keeps the diff readable.
- **Larger Pod range (`/14`)**: Would support up to 1,024 nodes. *Rejected* — current `/16` is enough headroom for years, and additional ranges can be added later without re-creating the cluster.

### D6: Cost-first defaults for reversible settings

**Decision:** Set the following to their cheapest options, accepting that they will be flipped when users arrive:
- `enablePrivateNodes: false` — public node IPs, no Cloud NAT (saves ~¥5,292/month NAT fixed cost).
- No Cloud NAT, no Cloud Router for prod in `network.ts`.
- Single Spot `e2-medium` node pool, autoscale 1-3 nodes, 30 GB pd-standard boot disks (mirrors dev).
- `managedPrometheus.enabled: false` (saves GMP ingestion + storage cost).
- `loggingConfig.enableComponents: ['SYSTEM_COMPONENTS', 'WORKLOADS']` — workloads logs needed for log-based alerts.
- `monitoringConfig.enableComponents: ['SYSTEM_COMPONENTS']` only.
- `costManagementConfig.enabled: true` (free).
- Release channel `REGULAR` (no cost difference; same upgrade tempo as dev).

**Why:** All of these are mutable post-creation per [GKE network-isolation docs](https://cloud.google.com/kubernetes-engine/docs/concepts/network-isolation) and standard Kubernetes API. Flipping them later requires Pulumi config changes and a `pulumi up`, not a cluster rebuild. Deferring them keeps first-month cost low.

**Trigger to flip:** "First real users arrive on prod" — at which point a separate OpenSpec change enables private nodes, provisions Cloud NAT, enables GMP, and adds a non-Spot pool for latency-sensitive workloads.

### D7: Skip cluster-level Confidential GKE Nodes; defer to per-pool

**Decision:** Do not set `confidentialNodes.enabled: true` at cluster level.

**Why:**
- Cluster-level Confidential Nodes is irreversible per [GKE Confidential Nodes docs](https://cloud.google.com/kubernetes-engine/docs/how-to/confidential-gke-nodes): *"This setting is irreversible."*
- Enabling forces all node pools onto N2D / C3 machine families (e2 is not supported), raising baseline node cost ~4-5x before the Confidential premium itself.
- Critically, Confidential Nodes does NOT solve the blockchain private-key-in-container-memory problem (a compromised container can still read its own memory). The right answer for blockchain keys is Cloud KMS asymmetric signing, where the key never leaves KMS.
- When blockchain mainnet GA arrives, a dedicated node pool with Confidential Nodes enabled (taint-isolated for the signing service) is more cost-efficient than cluster-wide enablement.

**Reversibility:** Cluster-level is irreversible; node-pool-level is additive and can be done later.

### D8: Single Pulumi component, env-aware (no refactor)

**Decision:** Extend the existing `KubernetesComponent` and `NetworkComponent` in `cloud-provisioning/src/gcp/components/` to handle prod, rather than creating a parallel `ProdKubernetesComponent`.

**Why:** Both components already have `environment === 'dev'` / `environment === 'prod'` branches in places. Adding prod branches alongside existing dev branches is a small, focused diff. Splitting into parallel components would duplicate the subnet, KMS, and Cluster wiring code unnecessarily.

**Alternative considered:**
- **Refactor into env-strategy classes** (one component per env): *Rejected* as scope creep. The current branching pattern is readable, and we should not refactor while simultaneously adding new functionality.

### D9: K8s manifests reuse dev overlays where possible

**Decision:** For each k8s namespace currently provisioned for dev (`backend`, `frontend`, `zitadel`, `argocd`, `external-secrets`, `reloader`, `atlas-operator`, `nats`, `keda`, `otel-collector`, `image-updater`), add a prod overlay only when its config differs from base. Where the base manifest is acceptable for prod as-is, no new overlay is created.

**Why:** The existing dev overlays already encode cost-focused overrides (Spot nodeSelector, replica reductions, disabled debug sidecars). Many of these are also appropriate for prod's cost-first phase. Only create a `prod/` overlay where prod actually diverges from base (e.g., different ingress hostnames, different secret references, different replica counts).

**Audit needed:** Each namespace's current overlay structure should be reviewed to determine whether a prod overlay needs to be authored, modified, or whether the base is sufficient.

## Risks / Trade-offs

- **[Risk] CIDR overlap with future VPC peering** → Mitigation: VPC peering between dev and prod is not currently planned. If future requirements introduce it, a new OpenSpec change reworks the CIDR plan (this would require both clusters to be re-created — large blast radius). Documented explicitly so future contributors understand the constraint.
- **[Risk] Public prod node IPs increase attack surface** → Mitigation: This is acceptable in the cost-first phase precisely because there are no users and no production data yet. The Pulumi deploy log for the first prod `pulumi up` should NOT include any references to "first user", "live traffic", or similar — those would be the trigger to flip `enablePrivateNodes: true`. Workload Identity is the primary defense even with public nodes.
- **[Risk] CMEK key deletion would brick the cluster** → Mitigation: The Cloud KMS key has Pulumi `deletionProtection` style guard (set `prevent_destroy` on the CryptoKey resource). Key version rotation is automatic and non-destructive. Manual key destruction would require an explicit Pulumi config flag.
- **[Risk] First `pulumi up` for prod is a large blast radius** → Mitigation: Per existing `deployment-infrastructure` spec, prod Pulumi deploys are manual-trigger only. The first prod `up` should be reviewed in the Pulumi Cloud preview before approval. Suggest doing it in stages: first the network + KMS + cluster, then a separate run for workload-related resources.
- **[Trade-off] Spot in prod = preemptions** → Acceptable in pre-launch phase. Preemptions during dogfooding are tolerable; the alternative (~50-100% additional Compute Engine cost for on-demand) is not justified before there are users.
- **[Trade-off] GMP disabled = no metric alerts in prod** → Acceptable pre-launch (log-based alerts cover ERROR conditions; latency/saturation alerts need GMP and will be enabled with users). The dev cluster has been running this way through Zitadel deployment and has been operationally sufficient.
- **[Risk] OpenSpec change "provision-prod-gcp-resources" implies cross-repo work** → The OpenSpec artifacts live in `specification/openspec/changes/`, but the actual Pulumi implementation lives in `cloud-provisioning/`. Mitigation: the implementation tasks reference cloud-provisioning paths explicitly; PR for cloud-provisioning will be reviewed and merged based on the specs in this change. The cross-repo coordination protocol from the workspace CLAUDE.md applies in modified form: this is NOT a proto change, so there is no BSR coordination needed, just specification ↔ cloud-provisioning PR pairing.

## Migration Plan

This is a green-field provisioning, not a migration. There is no existing prod infrastructure to transition from.

**Deployment order (single PR but recommend split Pulumi `up` runs):**

1. Merge this OpenSpec change to specification (no code-level effect; documentation only).
2. Merge cloud-provisioning PR that implements the prod branches in `kubernetes.ts`, `network.ts`, `postgres.ts`. Per existing `deployment-infrastructure` spec, this does NOT auto-deploy to prod.
3. Manually trigger `pulumi preview --stack prod` from Pulumi Cloud console. Review the full plan for unexpected destruction or replacement.
4. Manually trigger `pulumi up --stack prod`. Recommend approving in stages if Pulumi supports it:
   - Stage A: KeyRing + CryptoKey + IAM bindings (KMS first, so cluster creation can reference the key).
   - Stage B: VPC + Subnet + DNS zone + Certificate Manager (network).
   - Stage C: GKE Cluster + Node Pool (depends on Stage A + B).
   - Stage D: Cloud SQL, Artifact Registry, Service Accounts, Secret Manager.
   - Stage E: ArgoCD bootstrap + initial k8s namespaces.
5. Verify cluster creation succeeded by running `kubectl get nodes` against the prod cluster (after credential setup).
6. Verify `kubectl describe cluster` shows Dataplane V2 enabled and etcd CMEK key reference.
7. ArgoCD assumes responsibility for k8s manifest application; verify all Applications are syncing.

**Rollback strategy:**

- If Stage A-C fails or produces incorrect state: `pulumi destroy --stack prod --target <resource>` for the failed resource, fix Pulumi code, re-run `pulumi up`. Note: the KMS key has `prevent_destroy` — to destroy intentionally, remove the guard, then destroy in a separate Pulumi run.
- If the cluster is created but configured incorrectly on an irreversible setting (DPv2, CMEK, regional): destroy the cluster, fix Pulumi, re-create. This is the only safety valve.
- If reversible settings (Spot/private/NAT/GMP) are wrong: `pulumi up` with corrected config; cluster persists.

## Resolved Open Questions

All previously open questions have been resolved by the change author prior to implementation. Decisions and rationale are recorded below; the corresponding values are baked into the specs and tasks.

- **Q1: Cloud SQL instance tier for prod** → **`db-f1-micro`**. Same shared-core tier as dev. Cost-first phase; in-place tier upgrade is supported by Cloud SQL with seconds-to-minutes downtime, so under-sizing is recoverable without losing data.
- **Q2: DNS strategy for the prod apex `liverty-music.app`** → **Cloudflare remains authoritative for the apex**. Provision a Cloud DNS public zone for `api.liverty-music.app` and `auth.liverty-music.app` only; delegate just those subdomains from Cloudflare via NS records (same pattern as `dev.liverty-music.app`). Keeps Cloudflare's CDN/DDoS protection on the apex web traffic while letting Certificate Manager DnsAuthorization work against Cloud DNS for the GCP-fronted hostnames.
- **Q3: Initial `maxNodeCount` for the Spot pool** → **3** (same as dev). Mutable via Pulumi config; raise as workload count grows.
- **Q4: ArgoCD Applications scope for prod** → **Same set as dev** (`argocd`, `external-secrets`, `reloader`, `atlas-operator`, `nats`, `keda`, `otel-collector`, `image-updater`, `backend`, `frontend`, `zitadel`). Full parity simplifies the IaC diff and avoids "missing in prod" surprises later when workloads are exercised.
- **Q5: KMS key rotation period** → **90 days** (Cloud KMS recommended default). Sufficient for non-compliance phase; can be shortened via Pulumi config without re-creating the key.
