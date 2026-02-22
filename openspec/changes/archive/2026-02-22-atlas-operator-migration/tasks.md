## 1. Pulumi — postgres user password management (cloud-provisioning)

- [x] 1.1 Generate a random password for the `postgres` Cloud SQL user and store it in Pulumi config as a secret (`pulumi config set --secret postgresAdminPassword`)
- [x] 1.2 Add `gcp.sql.User` resource for `postgres` with `password` field in `src/gcp/components/postgres.ts` (depends on Cloud SQL instance)
- [x] 1.3 Add Secret Manager secret `postgres-admin-password` via existing `SecretConfig` pattern in `src/gcp/index.ts`
- [x] 1.4 Run `pulumi preview` and verify 2 new resources: `gcp.sql.User` (postgres) and `gcp.secretmanager.Secret` (password)

## 2. Remove @pulumi/postgresql provider (cloud-provisioning)

- [x] 2.1 Remove section 9 (PostgreSQL Schema & Permissions) from `src/gcp/components/postgres.ts` — pgProvider, appSchema, Grant, and 2 DefaultPrivileges resources
- [x] 2.2 Remove `import * as postgresql from '@pulumi/postgresql'` from `src/gcp/components/postgres.ts`
- [x] 2.3 Run `npm uninstall @pulumi/postgresql`
- [x] 2.4 Run `npm run typecheck` to verify no compilation errors

## 3. ESO — sync postgres password to K8s Secret (cloud-provisioning)

- [x] 3.1 Create new ExternalSecret `atlas-db-credentials` in `k8s/namespaces/backend/base/server/` that syncs `postgres-admin-password` from Secret Manager to K8s Secret key `POSTGRES_PASSWORD`
- [x] 3.2 Add IAM binding for ESO service account to access the new secret (via existing `SecretConfig.iamBindings` pattern)
- [x] 3.3 Verify with `kubectl kustomize k8s/namespaces/backend/overlays/dev`

## 4. Atlas Operator Helm chart (cloud-provisioning)

- [x] 4.1 Create `k8s/namespaces/atlas-operator/base/` with Kustomize + Helm configuration for Atlas Operator chart (`ariga/atlas-operator`)
- [x] 4.2 Create `k8s/namespaces/atlas-operator/overlays/dev/kustomization.yaml` with dev-specific resource limits
- [x] 4.3 Create ArgoCD Application `k8s/argocd-apps/dev/atlas-operator.yaml` pointing to `k8s/namespaces/atlas-operator/overlays/dev`
- [x] 4.4 Verify with `kubectl kustomize --enable-helm k8s/namespaces/atlas-operator/overlays/dev`

## 5. ArgoCD Application for backend migrations (cloud-provisioning)

- [x] 5.1 Create ArgoCD Application `k8s/argocd-apps/dev/backend-migrations.yaml` pointing to `liverty-music/backend` repo, path `k8s/atlas/overlays/dev`, namespace `backend`
- [x] 5.2 Verify the Application manifest renders correctly

## 6. Migration files — remove goose headers (backend)

- [x] 6.1 Remove `-- +goose Up` and `-- +goose Down` annotations from all 24 migration SQL files in `internal/infrastructure/database/rdb/migrations/versions/`
- [x] 6.2 Add schema bootstrap migration (new file, first in order) that creates `app` schema and grants permissions to the IAM SA user: `CREATE SCHEMA IF NOT EXISTS app`, `GRANT USAGE, CREATE ON SCHEMA app TO ...`, `ALTER DEFAULT PRIVILEGES ... GRANT ALL ON TABLES ...`, `ALTER DEFAULT PRIVILEGES ... GRANT ALL ON SEQUENCES ...`
- [x] 6.3 Regenerate `atlas.sum` by running `atlas migrate hash`

## 7. Remove goose from backend application (backend)

- [x] 7.1 Remove `RunMigrations()` call from `internal/di/provider.go`
- [x] 7.2 Remove `internal/infrastructure/database/rdb/migrate.go` (contains `RunMigrations`, `//go:embed`, goose Provider)
- [x] 7.3 Remove `NewStdlibDB()` from `internal/infrastructure/database/rdb/postgres.go` (migration-only DB connection)
- [x] 7.4 Remove `github.com/pressly/goose/v3` from `go.mod` (`go mod tidy`)
- [x] 7.5 Run `go test ./...` to verify no compilation errors or test failures

## 8. Atlas K8s manifests (backend)

- [x] 8.1 Create `k8s/atlas/base/kustomization.yaml` with `configMapGenerator` referencing all migration SQL files and `AtlasMigration` resource
- [x] 8.2 Create `k8s/atlas/base/atlas-migration.yaml` — `AtlasMigration` CRD with `urlFrom.secretKeyRef` pointing to `atlas-db-credentials`, `dir.configMapRef` pointing to migration ConfigMap
- [x] 8.3 Create `k8s/atlas/overlays/dev/kustomization.yaml` — patches for dev environment (secret name, sync wave annotation)
- [x] 8.4 Add `argocd.argoproj.io/sync-wave: "-1"` annotation to AtlasMigration (runs before backend Deployment)
- [x] 8.5 Verify with `kubectl kustomize k8s/atlas/overlays/dev`

## 9. Verification

- [x] 9.1 Run `pulumi preview` for cloud-provisioning changes (postgres user password, Secret Manager, remove postgresql provider)
- [x] 9.2 Run `pulumi up` after approval to apply infra changes
- [x] 9.3 Verify ESO syncs `atlas-db-credentials` secret to `backend` namespace
- [x] 9.4 Verify Atlas Operator pod is running in cluster
- [x] 9.5 Verify AtlasMigration CRD status shows all migrations applied
- [x] 9.6 Verify backend app starts successfully and API returns 200
