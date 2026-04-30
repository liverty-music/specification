## 1. Author the dev kube-dns-autoscaler override

- [x] 1.1 Create `cloud-provisioning/k8s/cluster/overlays/dev/kube-dns-autoscaler.yaml` containing a complete `kube-dns-autoscaler` ConfigMap manifest (namespace `kube-system`) whose `data.linear` JSON value declares `coresPerReplica: 256, nodesPerReplica: 16, preventSinglePointFailure: false`. Include `includeUnschedulableNodes: true` to match the existing GKE default (preserve all currently-set fields except the boolean we are flipping).
- [x] 1.2 Edit `cloud-provisioning/k8s/cluster/overlays/dev/kustomization.yaml`: add the new file path to the `resources` list (it is already registered for the dev `core` ArgoCD Application).

## 2. Validate the manifest locally

- [x] 2.1 Run `kubectl kustomize cloud-provisioning/k8s/cluster/overlays/dev` and verify the rendered output:
  - Includes the new `ConfigMap/kube-dns-autoscaler` in `kube-system`. ✓
  - The `data.linear` JSON contains `"preventSinglePointFailure":false`. ✓
  - All previously-rendered resources (the two `ClusterSecretStore` patches) still render unchanged. ✓
- [x] 2.2 Run `make check` in `cloud-provisioning` and confirm `lint-ts` exits 0. **Result: exits 0.**
- [x] 2.3 Run `kube-linter lint` against the rendered dev cluster overlay output and confirm no errors specific to the new manifest. **Result: `No lint errors found!`.**

## 3. Open and merge the PR

- [x] 3.1 Commit the two-file change on a feature branch with a Conventional Commits message (e.g., `feat(infra): override kube-dns-autoscaler in dev to drop replicas to 1`). **Commit: 943e6ef on branch `optimize-dev-kube-dns-replicas`.**
- [x] 3.2 Open a PR against `cloud-provisioning/main` titled with the commit subject. Include in the description: link to the proposal/design (this OpenSpec change), link to the GCP doc page authorizing the ConfigMap edit, expected post-merge effect (`kube-dns` Deployment 2→1, then cluster autoscaler 3→2 nodes after idle threshold). **PR: liverty-music/cloud-provisioning#210.**
- [x] 3.3 Wait for CI green (Buf checks skip; lint-ts pass; Pulumi preview shows no changes). Use `gh api repos/liverty-music/cloud-provisioning/pulls/N/comments` to fetch any inline review comments before merging — `gh pr view --json reviews` does not surface them. **Result: all CI checks SUCCESS (CI Success / Lint × 2 / changes / claude-review). Inline review comments via gh api: 0.**
- [x] 3.4 Merge the PR (merge commit; squash is disabled in cloud-provisioning). **Merged 2026-04-28T05:18:39Z.**

## 4. Verify post-merge behavior

- [x] 4.1 ArgoCD: verify the `core` Application reaches `Synced / Healthy` after the merge. Inspect the resource list for `ConfigMap/kube-dns-autoscaler` in `kube-system`. **Result: `Synced/Healthy`.**
- [x] 4.2 Verify the live ConfigMap: `kubectl get configmap kube-dns-autoscaler -n kube-system -o jsonpath='{.data.linear}'` SHALL contain `"preventSinglePointFailure":false`. **Result: `{"coresPerReplica":256,"includeUnschedulableNodes":true,"nodesPerReplica":16,"preventSinglePointFailure":false}`.**
- [x] 4.3 Wait up to 60 s for the autoscaler controller to reconcile, then verify `kubectl get deployment kube-dns -n kube-system` shows `READY: 1/1` (or `1/2` transitioning to 1). **Result: ConfigMap → false flip and kube-dns scale-down to 1/1 happened within ~30 s of ArgoCD sync.**
- [x] 4.4 Wait at least 10 minutes for the cluster autoscaler's idle threshold, then verify `kubectl get nodes -l cloud.google.com/gke-spot=true` shows 2 nodes (target). If still 3, run `kubectl describe nodes -l cloud.google.com/gke-spot=true | grep -A6 'Allocated resources'` to identify which node is still pinned and what workload is the new largest CPU consumer. **Result: 2 nodes (3rd node `d4xd` retired ~25 min after merge). Per-node CPU: 824m/940m (87%) and 790m/940m (84%) = 1614m total on 1880m capacity (86% packed, ~266m headroom).**
- [x] 4.5 Verify both spot nodes still use the optimize-dev-gke-cost disk config: `gcloud compute disks list --project liverty-music-dev --filter="name~^gke-standard-cluster--spot-pool"` shows 2 disks at 30 GB pd-standard. **Result: 2 × 30 GB pd-standard confirmed.**

## 5. Archive prep (post-soak)

- [ ] 5.1 After 24 h of stable 2-node operation, sync the new requirement into `openspec/specs/gke-standard-infrastructure/spec.md` and `git mv` this change to `openspec/changes/archive/YYYY-MM-DD-optimize-dev-kube-dns-replicas/` in a single archive PR.
- [ ] 5.2 The 2026-05-04 09:00 JST scheduled remote agent (routine `trig_019bjiY5CoQUYsPkVfxnNGTW`) will pick up the *combined* `optimize-dev-gke-cost` + this change's effect when it runs. No manual coordination required.
