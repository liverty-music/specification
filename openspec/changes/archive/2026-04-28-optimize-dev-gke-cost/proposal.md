## Why

The dev GCP project's Compute Engine spend jumped +1403% in the last 30 days (¥663 → ¥9,953/month). Investigation traced the spike to two compounding factors: GKE node boot disks defaulting to 100GB pd-balanced (~45% of the Compute Engine bill), and the Apr 21 self-hosted Zitadel deployment forcing a 3rd Spot node via 2 anti-affinity-spread API replicas. dev does not need HA or large boot volumes — these defaults are pure waste.

## What Changes

- **GKE Spot node pool boot disk SHALL be 30GB pd-standard** (down from default 100GB pd-balanced). E2 machine series does not support Hyperdisk per GCP documentation; pd-standard is the cheapest available type for E2.
- **Zitadel API and Login dev overlay replicas SHALL be reduced from 2 to 1**. The self-hosted Zitadel base manifests retain `replicas: 2` for staging/prod parity; only the dev overlay is patched.
- **Zitadel PodDisruptionBudget dev overlay SHALL relax `minAvailable` from 1 to 0**, since `replicas: 1 + minAvailable: 1` permanently blocks voluntary eviction (rolling updates, node drains, Spot preemption graceful handling).
- The `spot-pool` autoscaler `maxNodeCount: 3` setting is retained (raised from 2 on Apr 22 for Zitadel capacity); the autoscaler will downscale to 2 when total CPU requests fit. No spec change needed there.
- **NodePool boot disk update is in-place** (verified by `pulumi preview --stack dev`): `~ update` on `spot-pool-osaka` only, 206 other resources untouched. GKE rolls out the new disk template via surge upgrade, respecting PDBs.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `gke-standard-infrastructure`: Add a requirement specifying the Spot node pool boot disk size (30GB) and type (pd-standard), with the rationale that E2 does not support Hyperdisk.

## Impact

- **Affected code**:
  - `cloud-provisioning/src/gcp/components/kubernetes.ts` — add `diskSizeGb` and `diskType` to spot pool `nodeConfig`
  - `cloud-provisioning/k8s/namespaces/zitadel/overlays/dev/deployment-patch.yaml` — `replicas: 2 → 1`
  - `cloud-provisioning/k8s/namespaces/zitadel/overlays/dev/deployment-login-patch.yaml` — `replicas: 2 → 1`
  - `cloud-provisioning/k8s/namespaces/zitadel/overlays/dev/` — new `pdb-patch.yaml` + register in overlay `kustomization.yaml`
- **Affected systems**: dev GKE cluster `standard-cluster-osaka` only. Staging/prod unaffected (no overlay changes for those environments; node pool config is gated on `environment === 'dev'`).
- **Estimated savings**: ~¥3,800/month (boot disk) + ~¥1,700/month (Zitadel replica drops, conditional on autoscaler reaching 2 nodes) ≈ **~¥5,500/month**, lowering dev Compute Engine spend from ¥9,953 to an estimated ¥4,400.
- **Deployment risk**: brief (<90 s) per-pod eviction window during the GKE surge upgrade after the in-place NodePool update. Acceptable for dev. No data loss (boot disks are stateless; PVCs untouched).
- **Dependencies**: None — change is self-contained within `cloud-provisioning`.
