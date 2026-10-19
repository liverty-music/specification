## Why

Prod costs more than expected before launch. September's Kubernetes Engine net cost was ¥6,780. The cluster fee is covered by the GKE free tier, so the whole amount is Pod requests. About ¥2,100 of it came from Pods that preferred Spot but stayed on on-demand nodes from Sep 12 to 26. GKE fills existing on-demand capacity before it creates Spot nodes, and nothing moves Pods back.

The rest of the bill comes from three things:
- three hard-spread second replicas that always run on on-demand nodes
- the 1 GiB ephemeral-storage default on every container
- a few Pods with no remaining purpose

Outside the cluster, unused dev resources (a reserved static IP, Artifact Registry growth) and oversized prod storage add about ¥1,600–1,900 a month.

The same investigation found that the project's Compute Engine quotas, not GKE, had been blocking node upgrades and scale-up. Those quotas were raised during the `autonomous-incident-response` rollout. Autopilot's pre-provisioned capacity (balloon Pods) keeps consuming them.

There are no users yet, so availability can be traded for cost. The design has to work unchanged after launch, so the Spot-with-fallback mechanism is verified now rather than at launch.

## What Changes

- **Spot placement through a cluster-level default ComputeClass.**
  - A ComputeClass named `default` uses two `podFamily: general-purpose` rules: Spot first, then on-demand. It sets `activeMigration.optimizeRulePriority: true` and `whenUnsatisfiable: ScaleUpAnyway`.
  - Stateless workloads drop their per-namespace Spot patches and use this class. They run on Spot, fall back to on-demand when Spot is unavailable, and migrate back automatically when Spot returns.
  - NATS (StatefulSet with a PVC) keeps an explicit required-Spot nodeSelector. Google advises against active migration for stateful workloads.
  - Rollout is staged and verified:
    1. a throwaway non-default class proves that `podFamily` + `spot` works and that migration happens
    2. the cluster flag and `default` class are applied
    3. one low-risk workload moves first
    4. the rest follow
- **Single replicas.** `fan-api`, `fan-web-app` and `zitadel-api` go from 2 replicas to 1, and their hard topology spread (`DoNotSchedule` on hostname) is removed.
- **PDB fixes.**
  - The broken `zitadel-api-login` PDB is fixed. It has no `minAvailable`/`maxUnavailable` and allows 0 disruptions, which blocks draining its node.
  - Single-replica PDBs no longer block eviction.
- **Explicit requests.** Every container gets an explicit, small `ephemeral-storage` request instead of Autopilot's 1 GiB default.
- **Fewer Pods.**
  - Remove prod `cloud-sql-proxy`. It was a dev-only tool copied to prod. It has no Service, binds to localhost, saw zero connections in 30 days, and its prod path is broken. Developer DB access is redesigned in a separate change.
  - Disable the External Secrets validating webhook and cert-controller through chart values (`webhook.create: false`, `certController.create: false`). The two must go together: the webhook's `failurePolicy=Fail` rejects every ExternalSecret write if only its Pod stops.
  - Keep `reloader` (Secret rotation depends on it) and `argocd-server` (UI; small cost). Add comments to them and other support components stating what they are for.
- **Smaller fixes.**
  - Require Spot for the atlas `backend-migration-atlas-dev-db` Pod.
  - Set `ttlSecondsAfterFinished` on CronJob-created Jobs.
  - Turn off Autopilot proactive capacity provisioning (`--autopilot-general-profile=no-performance`). This reduces nodes, IPs and quota use; it does not change billing.
- **Non-Kubernetes savings.**
  - dev: release the unused reserved static IP `api-gateway-static-ip` and stop creating it.
  - dev and prod: add Artifact Registry cleanup policies.
  - prod: move the NATS PVC from `premium-rwo` (pd-ssd) to `standard-rwo` (JetStream data is recreated).
  - prod: set a Cloud SQL storage auto-increase limit.
  - prod: lengthen KMS key rotation to 365 days.

## Capabilities

### New Capabilities
<!-- none: infrastructure-only; no product behavior changes (skip_specs: true) -->

### Modified Capabilities
<!-- none -->

The spec tree describes product behavior (entities, usecases, adapters and screens). Nothing here changes it, so `.openspec.yaml` sets `skip_specs: true`.

## Impact

- **liverty-music/cloud-provisioning**
  - `src/gcp/`:
    - `clusterAutoscaling.defaultComputeClassEnabled` and the Autopilot general profile on the cluster
    - dev static IP creation
    - Artifact Registry cleanup policies
    - Cloud SQL `diskAutoresizeLimit`
    - KMS rotation period
  - `k8s/cluster/`: the `default` ComputeClass.
  - `k8s/namespaces/*/overlays/prod`:
    - Spot patches replaced
    - replicas, topology spread and PDB changes
    - ephemeral-storage requests
    - removals and comments
  - `k8s/namespaces/external-secrets/base/values.yaml`: webhook and cert-controller off. This also applies to dev.
  - `k8s/namespaces/nats/`: PVC storage class change, which needs a PVC re-create.
- **Runtime effects**
  - Each moved workload restarts once.
  - Spot preemptions now interrupt single replicas, which is accepted pre-launch.
  - NATS loses its JetStream data once.
  - The ArgoCD UI and the backend APIs have no redundancy.
- **Cost**
  - Kubernetes Pod cost: about ¥5,800/month → about ¥3,000/month (October run-rate basis).
  - Non-Kubernetes: about ¥1,600–1,900/month less, of which about ¥1,350 is dev.
- **Out of scope**
  - Developer access to Cloud SQL, to be unified across dev and prod in a separate change.
  - Load balancer and Cloud SQL tier changes. Consolidating forwarding rules saves nothing (the first five are one flat price), and Cloud SQL is already on the smallest tier.
