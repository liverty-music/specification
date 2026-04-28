## 1. Pulumi: GKE Spot node pool boot disk

- [x] 1.1 Edit `cloud-provisioning/src/gcp/components/kubernetes.ts`: in the `dev` branch's `gcp.container.NodePool` `nodeConfig`, add `diskSizeGb: 30` and `diskType: 'pd-standard'`.
- [x] 1.2 Run `make lint-ts` in `cloud-provisioning` to verify biome + tsc pass.
- [x] 1.3 Run `pulumi preview --stack dev` and confirm the plan shows `+- replace` (or `~ update`) on `spot-pool-osaka` only, with `diskSizeGb: 100 → 30` and `diskType: pd-balanced → pd-standard`. Verify no other resources are affected unexpectedly. **Result: `~ update` (in-place) — GKE handles via surge upgrade, no full NodePool replacement. Resources: 1 to update, 206 unchanged.**

## 2. Kubernetes: Zitadel dev overlay replicas → 1

- [x] 2.1 Edit `cloud-provisioning/k8s/namespaces/zitadel/overlays/dev/deployment-patch.yaml`: change `replicas: 2` to `replicas: 1`.
- [x] 2.2 Edit `cloud-provisioning/k8s/namespaces/zitadel/overlays/dev/deployment-login-patch.yaml`: change `replicas: 2` to `replicas: 1`.
- [x] 2.3 Update the comment in both patch files to reflect `replicaCount 1` (replacing the existing `replicaCount 2 to satisfy PDB minAvailable=1` rationale, since PDB will be relaxed below).

## 3. Kubernetes: Zitadel dev PDB relaxation

- [x] 3.1 Create `cloud-provisioning/k8s/namespaces/zitadel/overlays/dev/pdb-patch.yaml` with two PDB patches (`zitadel` and `zitadel-login`), each setting `spec.minAvailable: 0`.
- [x] 3.2 Edit `cloud-provisioning/k8s/namespaces/zitadel/overlays/dev/kustomization.yaml`: add `pdb-patch.yaml` to the `patches` (or `patchesStrategicMerge`) list following the existing patch entries' pattern.
- [x] 3.3 Run `kubectl kustomize cloud-provisioning/k8s/namespaces/zitadel/overlays/dev` and verify:
  - `Deployment/zitadel` shows `replicas: 1`. ✓
  - `Deployment/zitadel-login` shows `replicas: 1`. ✓
  - `PodDisruptionBudget/zitadel` shows `minAvailable: 0`. ✓
  - `PodDisruptionBudget/zitadel-login` shows `minAvailable: 0`. ✓
  - Spot nodeSelector and `enableServiceLinks: false` from base are preserved. ✓
- [x] 3.4 Run `make lint-k8s` (or the kube-linter step from `make lint`) and confirm zero errors. **Note: `make lint-k8s` fails on argocd overlay due to pre-existing Helm v4 incompatibility (unrelated to this change). Ran `kube-linter` on the rendered zitadel overlay directly: `No lint errors found!`. Spot nodeSelector check: `OK: All workloads have Spot VM nodeSelector.`**

## 4. Pre-merge validation

- [x] 4.1 Run `make check` in `cloud-provisioning` (lint-ts + lint-k8s) and confirm all checks pass. **Result: `make check` exits 0. (Pre-commit target only runs lint-ts; lint-k8s is broken by Helm v4 in argocd overlay — see 3.4 note.)**
- [x] 4.2 Open a PR against `cloud-provisioning/main`. Note in the description that the NodePool in-place update triggers a GKE surge upgrade (~90 s per-pod eviction window). **Result: liverty-music/cloud-provisioning#208 opened and merged 2026-04-27.**

## 5. Deploy and verify (post-merge)

- [x] 5.1 Monitor the auto-`pulumi up` job at https://app.pulumi.com/pannpers/liverty-music/dev/deployments until the NodePool in-place update and GKE surge upgrade complete successfully. **Result: Pulumi auto-deploy completed; boot disks reconfigured in-place.**
- [x] 5.2 Verify boot disks: `gcloud compute disks list --filter="name~^gke-standard-cluster--spot-pool"` shows all spot node disks at `SIZE_GB: 30` and `TYPE: pd-standard`. **Result: All 3 disks confirmed at 30 GB pd-standard.**
- [x] 5.3 Wait for ArgoCD to sync the `zitadel` Application after the cloud-provisioning merge. Verify `kubectl get deploy -n zitadel` shows both Deployments at `1/1`. **Result: zitadel 1/1, zitadel-login 1/1.**
- [x] 5.4 Verify `kubectl get pdb -n zitadel` shows both PDBs with `MIN AVAILABLE: 0`. **Result: both PDBs at 0.**
- [x] 5.5 Wait at least 15 minutes for the cluster autoscaler idle threshold, then run `kubectl get nodes -l cloud.google.com/gke-spot=true`. Record the node count (target: 2; acceptable: 3 if other workloads still pin a 3rd node). **Result: 3 nodes, 16 h after deploy. Per-node CPU requests: 639m / 709m / 940m = total 2288m, exceeding 2-node capacity (1880m) by 408m. The autoscaler is correctly keeping the 3rd node up because non-Zitadel workloads still need it. Boot-disk savings (¥3,800/month) are realized; the targeted Zitadel-replica savings (~¥1,700/month) are deferred until the largest non-Zitadel CPU consumers are right-sized — see task 6.2.**

## 6. Cost impact follow-up (after 7+ days)

- [ ] 6.1 Re-pull the GCP Billing report for the dev project, scoped to Compute Engine SKU. Compare daily Compute Engine cost from before the change vs the trailing 3-day average after the change. Target: ≥50% reduction. **Delegated to remote agent `verify-optimize-dev-gke-cost-savings` scheduled for 2026-05-04 09:00 JST (https://claude.ai/code/routines/trig_019bjiY5CoQUYsPkVfxnNGTW). Agent opens a verification issue on cloud-provisioning with paste-ready commands.**
- [ ] 6.2 If the autoscaler still pins 3 nodes (i.e., savings fall short), open a follow-up issue investigating which workload's CPU requests prevent compaction (likely candidates: cloud-sql-proxy Deployment, KEDA operator, OTel collector). **Pre-flagged: 5.5 already shows 3 nodes pinned. The 7-day reminder issue (task 6.1's agent) is the entry point for this investigation.**
