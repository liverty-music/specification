## 1. Verify manual IAM login through the proxy (prod, manual; D2, D4)

- [ ] 1.1 Create a temporary Pod from the D1 spec in `backend` with KSA `backend-app` (no `--auto-iam-authn`), port-forward it, and log in with `PGPASSWORD=$(gcloud sql generate-login-token) psql -h 127.0.0.1 -U pannpers@pannpers.dev -d liverty-music`. Verify the login succeeds, and record the command and output in the cloud-provisioning PR. If it fails, record the error and stop before group 2's dev Deployment removal
- [ ] 1.2 In that session, record `has_table_privilege` and `has_schema_privilege` results for `app` (expected outcome noted for D4), then delete the Pod. Verify that `kubectl get pod -n backend` no longer lists it

## 2. Proxy manifest, identity and runbook (cloud-provisioning; D1, D3, D5, D6)

- [ ] 2.1 Add the `db-proxy` GSA with `Roles.CloudSql.Client` only and its Workload Identity binding for `backend/db-proxy`, inside the `workloadEnabled` gate. Verify `pulumi preview` (prod) shows only these creates
- [ ] 2.2 Add `k8s/tools/db-proxy/base` (KSA with the GSA annotation, Pod per D1) and `overlays/{dev,prod}` setting the instance connection name and GSA email. Verify `kubectl kustomize` renders both overlays, and that ArgoCD Application sources do not include `k8s/tools/`
- [ ] 2.3 Write `docs/runbooks/cloud-sql-access.md` (prerequisites, the four commands, connection parameters, token expiry, break-glass login as `postgres`, adding a developer with the grant SQL, cleanup). Verify every command in it matches the manifest paths
- [ ] 2.4 Point `docs/runbooks/setup-prod-credentials.md` (postgres login) and `docs/runbooks/zitadel-break-glass.md` (rescue Pod) at the runbook and the manifest. Verify neither file still contains a laptop `cloud-sql-proxy` or a `kubectl run` proxy command
- [ ] 2.5 Remove `k8s/namespaces/backend/overlays/dev/sql-proxy/` and its kustomization entry. Verify the dev render no longer has a `cloud-sql-proxy` Deployment
- [ ] 2.6 Open the PR citing this change, merge after green CI and a clean preview; the user runs the prod `pulumi up`. Verify the `db-proxy` GSA exists in prod with only `roles/cloudsql.client`

## 3. Human read-only grants (backend; D4, D6)

- [ ] 3.1 Add the idempotent Atlas migration granting `USAGE`, `SELECT` on tables and sequences, and default privileges on `app` to roles matching `%@%` but not `%.iam`. Verify `atlas migrate lint` / the backend migration tests pass and the migration applies twice without error against Docker Compose Postgres (with a role named like an IAM user created for the test)
- [ ] 3.2 Replace `docs/dev-db-access.md` with a short pointer to the cloud-provisioning runbook. Verify the link resolves
- [ ] 3.3 Open the PR citing this change, merge after green CI, and verify the prod `AtlasMigration` reports the new version applied

## 4. End-to-end check

- [ ] 4.1 In prod, follow the runbook exactly: `apply -k`, `port-forward`, log in as `pannpers@pannpers.dev` with a token, verify that `SELECT` on an `app` table succeeds and `INSERT` fails with permission denied, and that `pg_stat_activity` shows the session as `pannpers@pannpers.dev`; then `delete -k` and verify the Pod is gone
- [ ] 4.2 On the next dev start, repeat 4.1 with the dev overlay and record the result in this change before archiving
