## Why

The Pulumi `@pulumi/postgresql` provider approach for managing PostgreSQL schema and permissions is blocked: Cloud SQL uses PSC-only connectivity (no public IP), making it impossible to connect from local machines or CI/CD. The Atlas Kubernetes Operator runs inside the GKE cluster where PSC connectivity is available, and can manage both schema creation and versioned migrations using the `postgres` superuser. This also replaces the goose v3 app-startup migration pattern with a GitOps-native approach.

## What Changes

- Install Atlas Kubernetes Operator in GKE via Helm
- Replace goose v3 app-startup migrations with Atlas Operator `AtlasMigration` CRD
- Remove `@pulumi/postgresql` provider and its schema/grant resources from Pulumi
- Set `postgres` user password on Cloud SQL and store in Secret Manager
- Create `app` schema, grants, and default privileges via Atlas migration files (run as `postgres` user)
- Migration files stored as ConfigMap in backend repo, synced by ArgoCD
- Remove `RunMigrations()` from Go application startup

## Capabilities

### New Capabilities

- `atlas-operator`: Kubernetes-native database schema management using Atlas Operator CRDs with versioned migrations stored as ConfigMaps

### Modified Capabilities

- `database`: Migration execution moves from app-startup goose to Atlas Operator; data resides in dedicated `app` schema
- `cloud-sql-connector`: Add `search_path=app` to DSN; postgres admin user requires password authentication
- `continuous-delivery`: ArgoCD syncs Atlas migration CRDs from backend repo; sync wave ordering ensures migrations run before app deployment

## Impact

- **cloud-provisioning**: Remove `@pulumi/postgresql` dependency; add postgres user password to Secret Manager; add Atlas Operator Helm chart to `k8s/namespaces/`; add ArgoCD Application for backend migrations
- **backend**: Add `k8s/atlas/` directory with AtlasMigration CRD, ConfigMap generator, and overlays; remove goose RunMigrations() and goose dependency; convert migration files from goose format to plain SQL
- **Operations**: No manual `pulumi up` with Auth Proxy required; migrations are fully automated via ArgoCD
