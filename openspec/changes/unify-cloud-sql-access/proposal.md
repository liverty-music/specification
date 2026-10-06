## Why

Developers reach Cloud SQL differently in dev and prod, and neither way works well.
- **Dev** keeps a standing `cloud-sql-proxy` Deployment with `--auto-iam-authn`. Everyone logs in as the shared `backend-app` workload identity, so an ad-hoc query cannot be told apart from application traffic in the audit logs.
- **Prod** has three documented paths, and none works end to end:
  - A copy of the dev Deployment. Its own manifest records that it fails with `role does not exist` (commit 698d62f, 2026-09-04). `optimize-prod-gke-cost` removes it.
  - A local `cloud-sql-proxy` without `--psc` (`setup-prod-credentials.md`). The instance accepts only Private Service Connect, so a laptop cannot reach it.
  - An ephemeral rescue Pod in `zitadel-break-glass.md`, written for dev only.

Google's guidance for private-IP / PSC-only instances is to connect through an intermediary inside the VPC and to log people in with IAM database authentication as themselves. There are no users yet, so the access path can be fixed now, before someone needs prod data under pressure.

## What Changes

- **One manifest for both environments.**
  - `k8s/tools/db-proxy/` in cloud-provisioning, with `base` and `overlays/{dev,prod}`, defines an ephemeral Cloud SQL Auth Proxy Pod.
  - The Pod uses `--psc` and no `--auto-iam-authn`, listens on `127.0.0.1:5432`, has a hard lifetime (`activeDeadlineSeconds`), and runs on Spot.
  - Developers create it with `kubectl apply -k`, reach it with `kubectl port-forward`, and delete it after use.
  - ArgoCD does not manage it.
- **Personal IAM login.**
  - Developers log in as their own Cloud SQL IAM user (`CLOUD_IAM_USER`, already provisioned from ESC `gcp.cloudSqlUsers`).
  - The password is a short-lived token from `gcloud sql generate-login-token`.
  - The proxy only carries the connection; it does not log in for the developer.
- **Read-only by default.**
  - Human IAM users get `USAGE` and `SELECT` on the `app` schema. A backend migration makes that grant idempotent, so it covers human users added later and tables created later.
  - Write access stays with the `postgres` break-glass credential.
- **Removals.**
  - The standing dev `cloud-sql-proxy` Deployment. Prod's is removed by `optimize-prod-gke-cost`.
  - The three conflicting procedures. One runbook replaces them; the backend `docs/dev-db-access.md` and `setup-prod-credentials.md` link to it, and `zitadel-break-glass.md` uses the same manifest with the `postgres` user.

## Capabilities

### New Capabilities
<!-- none: developer tooling and infrastructure only (skip_specs: true) -->

### Modified Capabilities
<!-- none -->

The spec tree describes product behavior. Developer database access is not product behavior, so `.openspec.yaml` sets `skip_specs: true`.

## Impact

- **liverty-music/cloud-provisioning**
  - New: `k8s/tools/db-proxy/` (base and dev/prod overlays) and a runbook.
  - Removed: `k8s/namespaces/backend/overlays/dev/sql-proxy/`.
  - Updated: `docs/runbooks/setup-prod-credentials.md` and `docs/runbooks/zitadel-break-glass.md`.
  - Possibly updated: the Cloud SQL IAM user list in ESC (prod and dev), if more developers are added.
- **liverty-music/backend**
  - An idempotent grant migration giving human IAM roles (`rolname LIKE '%@%'` and `NOT LIKE '%.iam'`) read-only access to the `app` schema.
  - `docs/dev-db-access.md` rewritten to point to the runbook.
- **Runtime**: no workload changes. The dev standing proxy (10m / 32Mi) goes away; the ephemeral Pod costs only while in use.
- **Dependencies**
  - Lands after `optimize-prod-gke-cost` removes the prod proxy Deployment.
  - The dev instance is stopped while dev workloads are disabled, so dev verification waits for the next dev window; prod is verified first.
