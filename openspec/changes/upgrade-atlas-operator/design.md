## Context

See proposal.md - Why. The operator is installed by kustomize `helmCharts` from `oci://ghcr.io/ariga/charts`, chart 0.7.23, with `prewarmDevDB: false`. Production migrations are one `AtlasMigration` (`backend-migration`, namespace `atlas-operator`). It is synced by the ArgoCD Application `backend-migrations` from backend `k8s/atlas/overlays/prod`, and it reads the `atlas-db-credentials` Secret (ExternalSecret from GSM `postgres-admin-password`). The dev GKE cluster does not exist today, so there is no environment to try the upgrade first.

## Goals / Non-Goals

**Goals:**
- Run the operator on 0.8.0, with Secret access limited to its own namespace.
- Remove the unused extension and the rollback snapshot table from prod.

**Non-Goals:**
- Atlas Pro features (drift checks, security scans) and moving the migration directory to the Atlas Registry.
- Spot placement of the dev-db Pod (owned by `optimize-prod-gke-cost`, task 1.7) and database access paths (owned by `unify-cloud-sql-access`).

## Decisions

**D1. Chart 0.8.0 with namespaced Secret access.**

`values.yaml` adds:

```yaml
rbac:
  clusterWideSecretAccess: false
watchNamespaces:
  - atlas-operator
```

`watchSecrets` is left unset. It defaults to `clusterWideSecretAccess`, so it becomes `false`, and the operator reads referenced Secrets with a plain `get` on every reconcile.

The chart notes that an `AtlasMigration` with a `configMapRef` directory stores its state in a Secret it owns. The operator therefore still needs `get`, `create` and `update` on Secrets in the namespaces it manages. A new `Role` and `RoleBinding` in `k8s/namespaces/atlas-operator/base/` grant exactly those three verbs on `secrets` in `atlas-operator` to the chart's ServiceAccount (`atlas-operator`).

Alternative: keep cluster-wide access and only bump the chart. It would be simpler, but the operator holds the superuser credential, so read access to every Secret in the cluster is the larger risk.

**D2. Drop the leftovers in one migration.** One file, `<timestamp>_drop_unused_uuid_ossp_and_series_backup.sql`:

```sql
DROP TABLE IF EXISTS "_series_consolidation_backup";
DROP EXTENSION IF EXISTS "uuid-ossp";
```

- `uuid-ossp`: no column default references `uuid_generate_*` (checked in prod), so the drop needs no `CASCADE`. A dependent object would make the migration fail loudly instead of removing it.
- The table: it has no dependents (checked in prod) and no code references.
- `schema.sql`: loses the table and its comments. It declares no extension today.
- Generating the file: `atlas migrate diff` produces the `DROP TABLE`. Atlas diffs the `app` schema only, so it may not emit the extension drop. In that case, add the `DROP EXTENSION` line by hand and run `atlas migrate hash`, so `atlas.sum` stays consistent and the repository drift check passes.

**D3. Rollout order.** Upgrade the operator first, migration second. The new migration then also serves as the first real apply on 0.8.0, which shows that the namespaced Role is sufficient: the operator must read the credential Secret and update its own state Secret. If the Role were missing a verb, the migration would fail with `TransientErr`, and the existing alert would fire.

## Risks / Trade-offs

- [No dev cluster to try 0.8.0 first] → `kubectl kustomize` render review and a server-side dry run against prod before merge. After sync, the follow-up migration exercises the full path. Rollback is reverting the chart version and values (CRDs are additive).
- [Namespaced Role misses a verb the operator needs] → it surfaces as a failed reconcile with `TransientErr` on the first migration, which alerts. The fix is to add the verb, or to temporarily restore `clusterWideSecretAccess: true`.
- [Rotating the `postgres` password no longer triggers a reconcile] → acceptable. Rotation is a manual break-glass procedure, and the next migration reads the new value.
- [The dropped snapshot is the last record of pre-consolidation series ids] → its comment declares it droppable once verified. The consolidation has been in prod since 2026-08-26 without a rollback, and Cloud SQL backups still hold it for their retention period.

## Migration Plan

1. cloud-provisioning PR: chart 0.8.0, values (D1), Role and RoleBinding. Before merge, check the render with `kubectl kustomize --enable-helm` and a server-side dry run against prod. After the ArgoCD sync, confirm that the operator Pod runs 0.8.0, logs no RBAC errors, and that `backend-migration` stays `Ready`.
2. backend PR: the D2 migration, `atlas.sum`, the kustomization file list and `schema.sql`. After the ArgoCD sync, confirm that `backend-migration` reports the new version as applied, and verify read-only in prod that `pg_extension` lists only `plpgsql` and that the table is gone.

Rollback: revert the cloud-provisioning PR. The migration is forward-only; recreating the extension or the table is a new migration.
