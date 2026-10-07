## Context

See proposal.md for the motivation. The facts below shape the approach. They were gathered on 2026-10-05/06 in `liverty-music-prod` from the billing export, live cluster reads and `liverty-music/cloud-provisioning` at `main`.

**Billing (Pod-based)**
- The cluster is GKE Autopilot, regional, version 1.35.8-gke.1380001. Every workload uses Pod-based billing on the general-purpose platform.
- Billed: Pod CPU, memory and ephemeral-storage requests. Not billed: nodes, node boot disks, node external IPs, unallocated capacity.
  - The pricing page says: "You are not charged for unmodified system DaemonSet Pods, operating system overhead, unallocated space, or unscheduled Pods … the underlying node size or quantity doesn't matter for billing."
  - The 30-day billing export confirms it: no VM, IP or boot-disk SKUs appear, and only the 10 GiB NATS PVC shows as PD.
- The $0.10/h cluster fee is fully offset by the GKE free tier.
- Measured unit prices:

  | Resource | On-demand | Spot |
  |---|---|---|
  | vCPU-hour | ¥9.1 | ¥2.7 |
  | GiB memory-hour | ¥0.94 | ¥0.30 |
  | GiB ephemeral-storage-hour | ¥0.028 | ¥0.028 |

- A minimum Pod (50m / 52Mi / 1Gi ephemeral) costs about ¥130/month on Spot and ¥390/month on-demand.

**Placement today**
- 26 of 29 user Pods sit on one Spot node.
- Spot settings vary by namespace:
  - Hard nodeSelector: nats, keda, otel-collector, reloader, atlas-operator, cloud-sql-proxy, zitadel hook Jobs.
  - Soft "prefer Spot" affinity plus a toleration: argocd, backend, frontend, zitadel Deployments, external-secrets.
- `fan-api`, `fan-web-app` and `zitadel-api` run 2 replicas with a hard hostname topology spread. With one Spot node, the second replica of each always lands on an on-demand node (210m / 400Mi).

**Requests**
- Autopilot raises every Pod to at least 50m CPU / 52 MiB and adds 1 GiB ephemeral storage to each container that does not set it.
- Sub-50m CPU requests in the manifests therefore save nothing.

**Disruption controls**
- The `zitadel-api-login` PDB has a selector but no `minAvailable`/`maxUnavailable`. Its status is `disruptionsAllowed: 0`.
- The single-replica Deployments with `minAvailable: 1` block eviction the same way.
- GKE's documented answer to the "prefer Spot" drift is active migration. Active migration does not evict Pods "if the eviction would violate a PodDisruptionBudget".

**Pre-provisioned capacity**
- Three on-demand `ek-*` nodes hold only system Pods and `gke-system-balloon-pod`s.
- The Autopilot overview says: "GKE also maintains a pool of pre-provisioned compute capacity … This extra compute capacity can increase IP address utilization … you can turn off proactive capacity provisioning by using the --autopilot-general-profile=no-performance flag."

**Quotas**: `SSD-TOTAL-GB` (1000) and `CPUS-ALL-REGIONS` (100) were raised during `autonomous-incident-response` and are managed by Pulumi. `IN_USE_ADDRESSES` (8) still caps the node count.

**Workload findings** (investigated 2026-10-06)
- `cloud-sql-proxy` was introduced as dev-only (`dev-db-local-access`) and later copied to prod without a stated reason.
- The ESO webhook and cert-controller came in as chart defaults.
- `reloader` implements the Secret-rotation decision of `secret-manager` (Decision 5).
- `argocd-server` serves only the port-forwarded UI.

## Goals / Non-Goals

**Goals:**
- Every user workload runs on Spot whenever Spot capacity exists, without per-workload Spot plumbing.
- Without Spot capacity, workloads fall back instead of going Pending, except NATS (D2). They return to Spot automatically.
- No billed request above what the workload needs, within Autopilot's minimums.
- The placement mechanism is the one the cluster keeps after launch; launch-time HA becomes a replica/PDB change, not a redesign.

**Non-Goals:**
- Changing Pod CPU/memory requests below Autopilot's minimum (no effect on billing).
- Developer access to Cloud SQL (separate change).
- Load balancer consolidation and Cloud SQL tier changes. The first five forwarding rules are one flat price, and the tier is already the smallest.
- Kyverno-style enforcement of the placement rules.

## Decisions

### D1: A cluster-level default ComputeClass instead of per-workload Spot selectors

**Chosen:** enable `clusterAutoscaling.defaultComputeClassEnabled` (gcloud `--enable-default-compute-class`) and create:

```yaml
apiVersion: cloud.google.com/v1
kind: ComputeClass
metadata:
  name: default
spec:
  autopilot:
    enabled: true
  priorities:
  - podFamily: general-purpose
    spot: true
  - podFamily: general-purpose
  activeMigration:
    optimizeRulePriority: true
  whenUnsatisfiable: ScaleUpAnyway
```

Stateless workloads drop their Spot nodeSelector, affinity and toleration patches, so they select no class and the default applies.

**Why:**
- *Required Spot for everything.* Google recommends it ("for all workloads that can tolerate disruptions well, you require Spot Pods"). But a Spot shortage then makes every workload Pending, including ArgoCD, which is the recovery path for everything else.
- *Preferred Spot (today).* It drifts to on-demand. The docs say "GKE prefers existing standard nodes that have allocatable capacity over creating new nodes for Spot Pods". That is the Sep 12–26 overspend.
- *The cluster autoscaler page* recommends exactly this pattern: priority rules favouring Spot, plus active migration.
- *Why cluster-level and not namespace-level or a named class.* A Pod that uses `podFamily` rules in a non-default custom ComputeClass gets a 0.5 vCPU / 0.5 GiB minimum. A namespace default counts as non-default, because GKE rewrites the Pod spec to select the class. That is about 10× today's 50m minimum. With the cluster-level default, the higher minimum applies only to Pods that use workload separation, Pod anti-affinity or extended run time. D3 removes the only spread constraints, and none of our Pods use the others.
- *`podFamily` over `machineFamily`.* `podFamily` rules keep Pod-based billing. `machineFamily` rules switch to node-based billing (the whole VM plus a premium), which costs far more for 50m Pods.
- *`ScaleUpAnyway`* follows the official default-class example, so Pods that cannot satisfy a rule still schedule.

**Unverified, hence D9:**
- No official example combines `podFamily` with `spot: true`, although the CRD lists both under `priorities[]`.
- Whether the billing SKU follows the Spot node.
- Whether migration actually happens for `podFamily` rules.
- That Pods under the cluster default keep the 50m minimum.
- Whether GKE adds the Spot toleration automatically.

**Known limitation:** "Custom ComputeClasses influence autoscaling decisions but are not considered by kube-scheduler". A Pod can still land on an existing on-demand node; active migration corrects it later.

### D2: NATS keeps an explicit required-Spot nodeSelector

NATS is a StatefulSet with a zonal 10 GiB PVC. The docs say: "To minimize the risk of data loss, don't enable active migration in ComputeClasses that stateful workloads use." An explicit `cloud.google.com/gke-spot: "true"` nodeSelector makes the Pod select the built-in `autopilot-spot` class, so the default class and its migration never apply to it. A Spot shortage leaves NATS Pending; async processing stalls and resumes. This is accepted before launch.

**Alternative rejected:** a second, migration-free custom class for NATS. It would be non-default, so the 0.5 vCPU minimum would apply: about ¥900/month more for a 50m Pod.

### D3: One replica, no hard spread, PDBs that allow eviction

- `fan-api`, `fan-web-app` and `zitadel-api` go to 1 replica, and their `topologySpreadConstraints` are removed.
  - The spread existed only to survive a single node loss.
  - Spread and anti-affinity also raise Autopilot minimums.
  - The original zitadel reason (bound the blast radius of the zitadel/zitadel#10103 wedge) matters only with users.
- PDBs on single-replica workloads are removed. The docs say: "Don't rely on PodDisruptionBudgets to protect workloads that … have only one instance."
- The broken `zitadel-api-login` PDB is fixed in the zitadel values: `minAvailable: 0` is dropped by the chart, so the PDB is disabled instead.
- The NATS PDB (`maxUnavailable: 1`) stays.
- These changes are a precondition for D1: active migration skips evictions that violate a PDB.
- **At launch:** restore 2 replicas, the spread with `whenUnsatisfiable: ScheduleAnyway` and `nodeTaintsPolicy: Honor` (per the Autopilot overview), and `minAvailable: 1` PDBs.

### D4: Explicit small ephemeral-storage requests

- Every container and init container sets `resources.requests.ephemeral-storage` (and an equal limit, which Autopilot enforces anyway).
- The default is 100Mi. Workloads that write to `emptyDir` or local caches (argocd repo-server, zitadel) get a size based on measured usage.
- Autopilot requires 10 MiB to 10 GiB per Pod.
- CPU and memory requests are left as they are: they already sit at or below the 50m / 52Mi floor.
- This saves about ¥550/month across about 30 containers.

### D5: Remove or disable Pods with no remaining purpose; document the ones that stay

| Workload | Action | Evidence |
|---|---|---|
| backend `cloud-sql-proxy` | remove from the prod overlay (dev untouched) | dev-only by design; no Service; `127.0.0.1` bind; 0 connections in 30 days; prod path broken |
| ESO webhook + cert-controller | `webhook.create: false`, `certController.create: false` in base values; drop their now-targetless resource patches | chart defaults never chosen; the controller does not need them |
| `argocd-server` | keep, 1 replica, comment | UI access; small cost |
| `reloader` | keep, comment | implements Secret rotation for 9 workloads |
| KEDA (3 Pods) | keep, comment | scales `media-consumer` 0↔1; removing it would make that Pod run 24/7 |

Why the ESO webhook and cert-controller go together:
- With the Pod at 0 replicas and the configuration left in place, `failurePolicy=Fail` rejects every ExternalSecret create, update or delete.
- Disabling only cert-controller leaves the CA bundle unmaintained.

Both are pruned in one ArgoCD sync, because the ValidatingWebhookConfiguration carries the ArgoCD tracking id.

### D6: Turn off proactive capacity provisioning

Set the Autopilot general profile to `no-performance`. This is billing-neutral, because unallocated capacity is not billed. It removes balloon-held nodes, which frees quota (`IN_USE_ADDRESSES`, `SSD-TOTAL-GB`, `CPUS-ALL-REGIONS`) and the node churn seen during upgrades. The cost is slower scale-up for general-purpose Pods.

The Pulumi field for this is not yet confirmed; see Open Questions. The gcloud flag is the documented interface.

### D7: Small Kubernetes hygiene

- The atlas `backend-migration-atlas-dev-db` Pod (500m / 2Gi while a migration plans) gets a required-Spot selector. It is short-lived, so preemption only retries the plan.
- CronJob `jobTemplate`s get `ttlSecondsAfterFinished` (e.g. 86400), so finished and failed Jobs stop accumulating.

### D8: Non-Kubernetes savings

| Item | Change | Saving/month |
|---|---|---|
| dev reserved static IP `api-gateway-static-ip` (unattached) | create only where the gateway uses it; release in dev | ¥1,147 |
| Artifact Registry (dev and prod) | cleanup policies: keep the most recent N versions per package, delete older than X days; dry-run first | ~¥290 |
| NATS PVC `premium-rwo` (860 KB used of 10 GiB) | re-create on `standard-rwo` | ~¥150–270 |
| Cloud SQL storage | set `diskAutoresizeLimit` (storage only grows) | avoids growth |
| KMS etcd key rotation 90 days | 365 days (each new version is billed while active) | stops +¥10/quarter |

**Not changed:**
- Forwarding rules: "First 5 forwarding rules $0.025 / 1 hour".
- Cloud SQL tier: already `db-f1-micro`.
- PSC Consumer End Point: has been ¥0 since Google reclassified it on 2026-09-30.
- Network Intelligence Center: discounted 100%.

### D9: Staged verification before relying on D1

| Step | What | Pass criteria | Blast radius |
|---|---|---|---|
| V1 | Throwaway non-default ComputeClass + scratch namespace. Start a Pod on an on-demand-only class, then patch the class to Spot-first + on-demand + `activeMigration` | the class is accepted; a new Spot node appears; the Pod moves to it (node label `cloud.google.com/gke-spot=true`); the Pod's requests show the non-default 0.5 vCPU minimum (doc check) | scratch only; tens of yen |
| V2 | Enable `defaultComputeClassEnabled` (Pulumi, prod `pulumi up`) and create the `default` class (ArgoCD, `k8s/cluster`) | the cluster reports the setting; no existing Pod changes (the docs say new Pods only) | none until Pods are re-created |
| V3 | Move `organizer-console-web-app` (drop its Spot patch) | the Pod runs on a Spot node; live requests stay 50m / 52Mi; Spot toleration present; NATS (explicit Spot) unaffected | one workload restart |
| V4 | Move the remaining stateless workloads, namespace by namespace, ArgoCD last | all user Pods except NATS select the default class; on-demand Pod mCPU in billing ≈ 0 the next day | per-namespace restarts |

If V1 fails (class rejected or no migration), fall back to required Spot (`nodeSelector`) for every workload, keep the D3–D8 work, and record the gap. If V3 shows a raised minimum, stop and revert that workload.

## Risks / Trade-offs

- [Spot shortage makes NATS Pending] → Accepted before launch. Alerts surface it (ArgoCD health, crash-loop alert). Other workloads fall back under D1.
- [Active migration evicts single replicas while moving back to Spot] → Accepted (no users). The 15-second Spot grace cap applies anyway.
- [`podFamily` + `spot` behaves differently from the docs' `machineFamily` examples] → V1 proves it before anything depends on it.
- [The default class unexpectedly applies the 0.5 vCPU minimum] → V3 checks live requests on one workload before V4.
- [kube-scheduler places Pods on existing on-demand nodes] → Active migration corrects it. Watch billing for on-demand mCPU.
- [ESO webhook removal lets an invalid ExternalSecret spec through] → ArgoCD shows the resulting `SecretSyncedError`. All ExternalSecrets are already in Git review.
- [Single replicas reduce availability] → Accepted pre-launch. D3 records how to restore HA at launch.
- [`no-performance` slows scale-up] → Acceptable at current scale. Revert with the same flag.
- [NATS PVC re-create loses JetStream data] → Acceptable before launch. Streams and consumers are recreated by NACK from Git.

## Migration Plan

1. **Kubernetes hygiene PR** (no class dependency):
   - D3 replicas, spread and PDB changes
   - D4 ephemeral-storage requests
   - D5 removals and comments
   - D7 atlas dev-db Spot and Job TTL

   Existing Spot patches stay for now.
2. **V1** in a scratch namespace (manual, recorded in tasks).
3. **Pulumi PR:**
   - `defaultComputeClassEnabled`
   - Autopilot general profile `no-performance` (D6)
   - D8 Pulumi items (dev static IP, AR cleanup policies, Cloud SQL autoresize limit, KMS rotation)

   Then prod `pulumi up`.
4. **ArgoCD PR:** the `default` ComputeClass in `k8s/cluster`. Then V2.
5. **V3 PR:** `organizer-console-web-app` drops its Spot patch. Verify.
6. **V4 PRs:** remaining namespaces drop their Spot patches. NATS keeps its explicit selector.
7. **NATS PVC re-create** on `standard-rwo` (D8), done during a quiet window.

**Rollback:**
- Each Kubernetes step reverts via Git.
- Deleting the `default` ComputeClass restores built-in behaviour for newly created Pods.
- `defaultComputeClassEnabled: false` and the general profile revert through Pulumi.

## Open Questions

- The Pulumi field for the Autopilot general profile (`no-performance`). If the provider lacks it, apply it with gcloud and record it in the runbook, as with other out-of-band settings.
  - **Resolved:** no provider has it (`@pulumi/gcp` 9.37 and 10.0.0; hashicorp/terraform-provider-google#26958). Applied with gcloud, recorded in `docs/runbooks/gke-autopilot-general-profile.md`. A `command.local.Command` wrapper was considered and not adopted.
- Artifact Registry retention numbers (versions to keep, age). To be chosen from rollback needs during implementation, with a dry-run first.
  - **Resolved:** prod keeps 30 versions and deletes older than 60 days; dev keeps 15 and deletes older than 14 days. `keepCount` counts versions, and each release pushes three (index, image, attestation), so this keeps about 10 / 5 releases. The dry run logged nothing (Data Access audit logs are off), so the policies were replayed over the version listings before enforcing.

## Implementation findings

- **ArgoCD diff/apply mismatch.** Six Applications synced with client-side apply under the cluster-wide Server-Side Diff, which never detects a change that only removes fields (argoproj/argo-cd#23845). Dropping a Spot patch therefore stayed `Synced` without applying. Fixed by moving every Application to Server-Side Apply (cloud-provisioning#594).
- **Prod Applications were not GitOps-managed.** Prod had no root app, so `k8s/argocd-apps/prod` never reached the cluster. A root app per environment now ships in the argocd overlay (cloud-provisioning#595).
- **Default-class Spot nodes need no Spot toleration.** Pods placed by the `default` class run on Spot without one (V3), and Autopilot's 25s grace-period cap for Spot-tolerating Pods no longer applies.
- **Soft podAntiAffinity kept the 50m minimum** on the default class (observed on the Argo CD Pods, which carry the chart's preferred podAntiAffinity).
