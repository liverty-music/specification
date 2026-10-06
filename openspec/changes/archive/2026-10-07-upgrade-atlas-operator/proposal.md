## Why

The Atlas Kubernetes Operator runs at chart 0.7.23 and applies every production migration as the `postgres` superuser. Releases up to 0.8.0 fix CVEs in the bundled atlas-cli and openssl, and let the operator run without cluster-wide access to Secrets.

The v0.8 headline features need Atlas Pro and are left out: pre-apply drift checks, `AtlasDriftCheck` and `AtlasSecurityScan`. They cost about $68 a month for dev and prod. Few paths can cause drift. The only extension a security scan could inspect, `uuid-ossp`, is no longer used.

The production database also still carries two leftovers:

- `uuid-ossp`: no column default has used it since UUIDv7 ids moved to the application (migration `20260311171822_enforce_uuidv7_and_cleanup`).
- `_series_consolidation_backup`: a one-time rollback snapshot of 956 rows from the series consolidation of 2026-08-26, which its own comment marks as droppable once verified.

## What Changes

- Upgrade the atlas-operator Helm chart from 0.7.23 to 0.8.0.
- Remove the operator's cluster-wide Secret access:
  - Set `rbac.clusterWideSecretAccess: false` and `watchNamespaces: [atlas-operator]`.
  - Add a namespaced Role and RoleBinding that grant `get`, `create` and `update` on Secrets in `atlas-operator`.
  - Rotating the `postgres` password no longer triggers a reconcile by itself; the next reconcile reads the new value.
- Add one backend migration that drops the `uuid-ossp` extension and the `_series_consolidation_backup` table, and remove both from the desired-state schema.

The id rules do not change. Every `id` column already has no default and is NOT NULL, and every entity table has the UUIDv7 check (verified read-only in prod on 2026-10-06: 24 of 24 id columns NOT NULL without a default, 23 of 23 entity tables with the check).

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none) No product behavior changes. The change touches deployment tooling, cluster access and unused database objects, so `skip_specs: true` is set.

## Impact

- cloud-provisioning:
  - `k8s/namespaces/atlas-operator/base/kustomization.yaml` (chart version) and `values.yaml` (RBAC and watch scope)
  - a new namespaced Role and RoleBinding
- backend:
  - a new migration in `k8s/atlas/base/migrations/` plus `atlas.sum` and the kustomization file list
  - `internal/infrastructure/database/rdb/schema/schema.sql`
- No application code, API or proto change.
- The existing "Atlas Operator Migration Failure" alert keeps working: the 0.8.0 controller still emits the `TransientErr` and `BackoffLimitExceeded` reasons it matches.
