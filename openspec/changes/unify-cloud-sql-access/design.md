## Context

See proposal.md for the motivation. The facts below were checked on 2026-10-06.

**Instances**
- `postgres-osaka` in both projects is PSC-only (`pscEnabled: true`, no public or private IP).
- `cloudsql.iam_authentication` is `on`.
- The dev instance is currently `STOPPED` (`activationPolicy: NEVER`) and the dev cluster does not exist (`workloadEnabled: false`).

**Database users (prod)**
- Six `CLOUD_IAM_SERVICE_ACCOUNT` users: `backend-app`, `fan-api`, `admin-console-api`, `organizer-console-api`, `media-consumer`, `zitadel`.
- One `CLOUD_IAM_USER`: `pannpers@pannpers.dev`. It comes from ESC `gcp.cloudSqlUsers` through `postgres.ts` and also holds `roles/cloudsql.instanceUser`.
- The `postgres` built-in user.

**Grants**
- `20260223120000_grant_iam_users_app_schema.sql` gave `USAGE` and `SELECT` on `app`, plus default privileges, to every role that matched `%@%` *at the time it ran*.
- Later grant migrations loop over `%@%.iam` only, which is service accounts.
- Whether the prod `pannpers@pannpers.dev` role holds these grants depends on whether it existed when that migration first ran in prod. That is unknown.

**Current access paths**
- dev Deployment: `--psc --auto-iam-authn`, running as KSA `backend-app`.
- prod copy of that Deployment: recorded as failing with `role does not exist` (698d62f). There is no matching error in the last 30 days of Cloud SQL logs, so the cause is unconfirmed. `optimize-prod-gke-cost` removes it.
- Laptop proxy without `--psc` (`setup-prod-credentials.md`): cannot reach a PSC-only instance.
- `kubectl run` rescue Pod in `zitadel-break-glass.md` (dev only).

**What the docs say**
- Cloud SQL IAM login: "For an IAM [user], the username is the full email address of the user." With manual IAM authentication, a token from `gcloud sql generate-login-token` is the password.
- Automatic IAM authentication (proxy README): "Make sure to run the Proxy as the same IAM principal as the database user you want to log in as."
- Proxy authentication "is separate from database user authentication".
- No official page shows manual IAM login *through* the proxy. The pass-through itself is proven in this repository: the break-glass procedure and the `zitadel-db-grant` Job run the proxy without `--auto-iam-authn` and log in as `postgres` with a password.

## Goals / Non-Goals

**Goals:**
- One procedure and one manifest for dev and prod, differing only by overlay.
- Every human session logs in as that person's own Cloud SQL IAM user, so audit logs and `pg_stat_activity` name the person.
- Human IAM users are read-only on `app` by default.
- Nothing runs when nobody is connected.

**Non-Goals:**
- Write access for humans through IAM. Writes use the `postgres` break-glass credential, as today.
- Cloud SQL IAM group authentication (`CLOUD_IAM_GROUP`). It is worth adopting once there is more than one developer; see Open Questions.
- Cloud SQL Studio or other console access paths.
- Local Docker Compose Postgres (unchanged).

## Decisions

### D1: An ephemeral proxy Pod inside the cluster, created from a kustomize manifest

**Chosen:** `k8s/tools/db-proxy/` in cloud-provisioning defines one Pod (not a Deployment) named `db-proxy` in the `backend` namespace:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: db-proxy
  labels:
    app.kubernetes.io/name: db-proxy
spec:
  serviceAccountName: db-proxy
  activeDeadlineSeconds: 7200
  restartPolicy: Never
  nodeSelector:
    cloud.google.com/gke-spot: "true"
  containers:
  - name: cloud-sql-proxy
    image: gcr.io/cloud-sql-connectors/cloud-sql-proxy:2
    args: ["--psc", "--address=127.0.0.1", "--port=5432", "<instance>"]
```

- The overlays (`dev`, `prod`) set the instance connection name.
- Usage:
  1. `kubectl apply -k k8s/tools/db-proxy/overlays/<env>`
  2. `kubectl port-forward pod/db-proxy 5432:5432 -n backend`
  3. `psql`
  4. `kubectl delete -k …` when done
- `activeDeadlineSeconds` ends a forgotten Pod after two hours.
- ArgoCD does not include `k8s/tools/`, so it never re-creates or prunes the Pod.
- `--address=127.0.0.1` keeps the port reachable only through `port-forward`, never from other Pods.

**Why:**
- Google's guidance for private connectivity is to connect through an intermediary inside the VPC. A GKE Pod reached with `port-forward` is that intermediary, with no bastion VM to patch.
- A laptop proxy cannot reach PSC endpoints.
- The user preferred a manifest to a script: `apply -k` is declarative, reviewable and the same command in both environments.

**Alternatives rejected:**
- A standing Deployment (today's dev): it costs money while idle and invites shared use.
- `kubectl run` with inline flags (today's break-glass): this is the drift that produced three procedures.
- A bastion VM with IAP TCP forwarding: an extra VM and OS to maintain, for the same result.

### D2: The proxy does not log anyone in (`--auto-iam-authn` is off)

- With `--auto-iam-authn`, the proxy logs in as its own principal, so every session would become the Pod's service account.
- Logging in as a person would then need a proxy running as that person's identity, but Workload Identity maps a KSA to a GSA, never to a human account.
- Without the flag, the proxy only authorizes the connection and encrypts it. The client sends the database username and password:
  - username: the person's email
  - password: `$(gcloud sql generate-login-token)`
- The token expires after about one hour, which limits only new connections. Developers run `generate-login-token` again before reconnecting.

### D3: A dedicated `db-proxy` service account that can connect but cannot log in

- Pulumi creates GSA `db-proxy` in each project, using the existing `iamSvc.createServiceAccount`, `bindProjectRoles([Roles.CloudSql.Client])` and `bindKubernetesSaUser('db-proxy', …, 'backend')` helpers.
- It has **no** `cloudsql.instanceUser` role and no Cloud SQL user.
- The manifest defines the matching KSA with the `iam.gke.io/gcp-service-account` annotation.

**Why not reuse `backend-app`:** that identity holds write grants on `app`. If someone later added `--auto-iam-authn` to the Pod, every session would silently become the application. A connect-only identity makes that mistake fail closed.

The binding is inside the existing `workloadEnabled` gate, like the other workload identities.

### D4: Read-only grants for human IAM users through a backend migration

- A new Atlas migration in `backend/k8s/atlas/base/migrations/` loops over `pg_roles` where `rolname LIKE '%@%' AND rolname NOT LIKE '%.iam'`, i.e. human IAM users only. For each role it grants:
  - `GRANT USAGE ON SCHEMA app`
  - `GRANT SELECT ON ALL TABLES IN SCHEMA app`
  - `GRANT SELECT ON ALL SEQUENCES IN SCHEMA app`
  - `ALTER DEFAULT PRIVILEGES IN SCHEMA app GRANT SELECT ON TABLES` and `… ON SEQUENCES`
- The migration is idempotent, like the existing grant loops.
- It runs as `postgres`, the owner of every `app` object, so the default privileges cover future tables.

**Adding a developer later:**
1. Add the email to ESC `gcp.cloudSqlUsers`.
2. Run `pulumi up` to create the user.
3. Run the same grant block once as `postgres` through `db-proxy`; the runbook carries the SQL.

A one-person team does not justify a repeating grant Job. IAM groups (Open Questions) remove this step.

**Alternative rejected:** an ArgoCD Sync-hook grant Job like `zitadel-db-grant`. It would need the `postgres` password Secret in another namespace, and its re-run benefit only matters with frequent user changes.

### D5: Break-glass uses the same Pod

`zitadel-break-glass.md` and the `postgres` section of `setup-prod-credentials.md` switch to `kubectl apply -k k8s/tools/db-proxy/overlays/<env>` and log in as `postgres` with the password from Secret Manager. The pass-through behaviour that D2 relies on is the same behaviour these procedures rely on today.

### D6: One runbook, linked from every entry point

- The new `docs/runbooks/cloud-sql-access.md` in cloud-provisioning covers:
  - prerequisites (cluster credentials, Cloud SQL IAM user, `roles/cloudsql.instanceUser`)
  - the four commands
  - connection parameters (`search_path=app`, `sslmode=disable`, since the proxy encrypts)
  - token expiry
  - break-glass login
  - adding a developer
  - cleanup
- backend `docs/dev-db-access.md` becomes a short pointer to it.

## Risks / Trade-offs

- [Manual IAM login through the proxy does not work (no doc example)] → Task 1 verifies it in prod before anything else changes. If it fails, record the error, keep the manifest and break-glass parts, and revisit the login method before removing the dev Deployment.
- [The pannpers prod role lacks grants today] → D4's migration fixes it. Task 1 records the before and after (`has_table_privilege`).
- [A forgotten Pod keeps a tunnel open] → `activeDeadlineSeconds: 7200`. Spot preemption also ends it.
- [`kubectl apply -k` needs Pod-create rights in `backend`] → Only cluster admins hold them today. Acceptable for one developer.
- [Token expiry interrupts long sessions] → Only new connections need a token. Documented in the runbook.
- [Dev cannot be verified while dev is down] → Prod is verified first. The dev overlay is a single-field change; it is verified on the next dev start (a task left open until then).

## Migration Plan

1. **Verify (prod)**, before any merge: create a Pod by hand from the D1 spec (KSA `backend-app` for now) and log in as `pannpers@pannpers.dev` with a token. Record the result and the role's current grants.
2. **cloud-provisioning PR:**
   - `db-proxy` GSA, IAM role and Workload Identity binding
   - `k8s/tools/db-proxy/` base and overlays, with the KSA
   - runbook, and updates to `setup-prod-credentials.md` and `zitadel-break-glass.md`
   - removal of `k8s/namespaces/backend/overlays/dev/sql-proxy/`

   Merge; the user runs the prod `pulumi up`.
3. **backend PR:** the human read-only grant migration and the `docs/dev-db-access.md` pointer. Merge; the prod migration applies through atlas-operator.
4. **Verify (prod)** with the real manifest: `apply -k`, `port-forward`, log in, `SELECT` on an `app` table succeeds, `INSERT` fails, then `delete -k`.
5. **Verify (dev)** on the next dev start.

**Rollback:** delete the Pod, revert the PRs. The grant migration is additive; revoking is a follow-up migration if ever needed.

## Open Questions

- IAM group authentication: if `pannpers.dev` has Cloud Identity / Workspace groups, a `CLOUD_IAM_GROUP` user with grants on the group role removes the per-developer grant step. Deferred until there is a second developer.
