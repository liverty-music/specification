## 1. Pulumi — postgres user password management (cloud-provisioning)

- [ ] 1.1 Generate a random password for the `postgres` Cloud SQL user and store it in Pulumi config as a secret (`pulumi config set --secret postgresAdminPassword`)
- [ ] 1.2 Add `gcp.sql.User` resource for `postgres` with `password` field in `src/gcp/components/postgres.ts` (depends on Cloud SQL instance)
- [ ] 1.3 Add Secret Manager secret `postgres-admin-password` via existing `SecretConfig` pattern in `src/gcp/index.ts`
- [ ] 1.4 Run `pulumi preview` and verify 2 new resources: `gcp.sql.User` (postgres) and `gcp.secretmanager.Secret` (password)

## 2. Remove @pulumi/postgresql provider (cloud-provisioning)

- [ ] 2.1 Remove section 9 (PostgreSQL Schema & Permissions) from `src/gcp/components/postgres.ts` — pgProvider, appSchema, Grant, and 2 DefaultPrivileges resources
- [ ] 2.2 Remove `import * as postgresql from '@pulumi/postgresql'` from `src/gcp/components/postgres.ts`
- [ ] 2.3 Run `npm uninstall @pulumi/postgresql`
- [ ] 2.4 Run `npm run typecheck` to verify no compilation errors

## 3. ESO — sync postgres password to K8s Secret (cloud-provisioning)

- [ ] 3.1 Create new ExternalSecret `atlas-db-credentials` in `k8s/namespaces/backend/base/server/` that syncs `postgres-admin-password` from Secret Manager to K8s Secret key `POSTGRES_PASSWORD`
- [ ] 3.2 Add IAM binding for ESO service account to access the new secret (via existing `SecretConfig.iamBindings` pattern)
- [ ] 3.3 Verify with `kubectl kustomize k8s/namespaces/backend/overlays/dev`

## 4. Atlas Operator Helm chart (cloud-provisioning)

- [ ] 4.1 Create `k8s/namespaces/atlas-operator/base/` with Kustomize + Helm configuration for Atlas Operator chart (`ariga/atlas-operator`)
- [ ] 4.2 Create `k8s/namespaces/atlas-operator/overlays/dev/kustomization.yaml` with dev-specific resource limits
- [ ] 4.3 Create ArgoCD Application `k8s/argocd-apps/dev/atlas-operator.yaml` pointing to `k8s/namespaces/atlas-operator/overlays/dev`
- [ ] 4.4 Verify with `kubectl kustomize --enable-helm k8s/namespaces/atlas-operator/overlays/dev`

## 5. ArgoCD Application for backend migrations (cloud-provisioning)

- [ ] 5.1 Create ArgoCD Application `k8s/argocd-apps/dev/backend-migrations.yaml` pointing to `liverty-music/backend` repo, path `k8s/atlas/overlays/dev`, namespace `backend`
- [ ] 5.2 Verify the Application manifest renders correctly

## 6. Migration files — remove goose headers (backend)

- [ ] 6.1 Remove `-- +goose Up` and `-- +goose Down` annotations from all 24 migration SQL files in `internal/infrastructure/database/rdb/migrations/versions/`
- [ ] 6.2 Add schema bootstrap migration (new file, first in order) that creates `app` schema and grants permissions to the IAM SA user: `CREATE SCHEMA IF NOT EXISTS app`, `GRANT USAGE, CREATE ON SCHEMA app TO ...`, `ALTER DEFAULT PRIVILEGES ... GRANT ALL ON TABLES ...`, `ALTER DEFAULT PRIVILEGES ... GRANT ALL ON SEQUENCES ...`
- [ ] 6.3 Regenerate `atlas.sum` by running `atlas migrate hash`

## 7. Remove goose from backend application (backend)

- [ ] 7.1 Remove `RunMigrations()` call from `internal/di/provider.go`
- [ ] 7.2 Remove `internal/infrastructure/database/rdb/migrate.go` (contains `RunMigrations`, `//go:embed`, goose Provider)
- [ ] 7.3 Remove `NewStdlibDB()` from `internal/infrastructure/database/rdb/postgres.go` (migration-only DB connection)
- [ ] 7.4 Remove `github.com/pressly/goose/v3` from `go.mod` (`go mod tidy`)
- [ ] 7.5 Run `go test ./...` to verify no compilation errors or test failures

## 8. Atlas K8s manifests (backend)

- [ ] 8.1 Create `k8s/atlas/base/kustomization.yaml` with `configMapGenerator` referencing all migration SQL files and `AtlasMigration` resource
- [ ] 8.2 Create `k8s/atlas/base/atlas-migration.yaml` — `AtlasMigration` CRD with `urlFrom.secretKeyRef` pointing to `atlas-db-credentials`, `dir.configMapRef` pointing to migration ConfigMap
- [ ] 8.3 Create `k8s/atlas/overlays/dev/kustomization.yaml` — patches for dev environment (secret name, sync wave annotation)
- [ ] 8.4 Add `argocd.argoproj.io/sync-wave: "-1"` annotation to AtlasMigration (runs before backend Deployment)
- [ ] 8.5 Verify with `kubectl kustomize k8s/atlas/overlays/dev`

## 9. Verification

- [ ] 9.1 Run `pulumi preview` for cloud-provisioning changes (postgres user password, Secret Manager, remove postgresql provider)
- [ ] 9.2 Run `pulumi up` after approval to apply infra changes
- [ ] 9.3 Verify ESO syncs `atlas-db-credentials` secret to `backend` namespace
- [ ] 9.4 Verify Atlas Operator pod is running in cluster
- [ ] 9.5 Verify AtlasMigration CRD status shows all migrations applied
- [ ] 9.6 Verify backend app starts successfully and API returns 200
