## 1. Operator upgrade (cloud-provisioning)

- [ ] 1.1 Bump the atlas-operator chart in `k8s/namespaces/atlas-operator/base/kustomization.yaml` to 0.8.0 and add the D1 values. Verify that `kubectl kustomize --enable-helm` on the prod overlay renders:
  - the 0.8.0 image
  - a ClusterRole without `secrets`
  - the `--watch-namespaces` (or equivalent) setting for `atlas-operator`
- [ ] 1.2 Add the namespaced Role (`get`, `create` and `update` on `secrets`) and the RoleBinding to the chart ServiceAccount, and list them in the base kustomization. Verify the render includes both, and that `kubectl auth can-i get secrets --as=system:serviceaccount:atlas-operator:atlas-operator -n atlas-operator` is yes while the same check in `backend` is no (server-side dry run against prod).
- [ ] 1.3 Open the PR, get CI green (`make lint`, including the Spot and kubeconform checks) and merge. Verify that ArgoCD is Synced on the merge commit, the operator Pod logs the 0.8.0 version with no RBAC errors, and `kubectl -n atlas-operator get atlasmigration backend-migration` stays `Ready`.

## 2. Drop unused database objects (backend)

- [ ] 2.1 Remove `_series_consolidation_backup` from `internal/infrastructure/database/rdb/schema/schema.sql`. Generate the D2 migration with `atlas migrate diff --env local`; if the extension drop is missing, add it by hand and run `atlas migrate hash`. Add the file to the `k8s/atlas/base/kustomization.yaml` file list. Verify that `atlas migrate validate --env local`, `atlas migrate apply --env local` and the Atlas CI drift check pass.
- [ ] 2.2 Open the PR, get CI green and merge. After the ArgoCD sync, verify that `backend-migration` reports the new version applied. Then verify read-only in prod that `pg_extension` lists only `plpgsql`, that `_series_consolidation_backup` no longer exists, and that no alert fired.
