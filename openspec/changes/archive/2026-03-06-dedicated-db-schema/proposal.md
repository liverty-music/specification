## Why

The dev Cloud SQL (PostgreSQL 18) denies `CREATE` on the `public` schema to IAM-authenticated users, blocking Atlas migrations. PostgreSQL 15+ revokes default `CREATE` privileges on `public` from non-superusers. The database had no tables yet, making this the ideal time to adopt a dedicated `app` schema instead of patching `public` permissions.

## What Changes

- Introduce Pulumi `@pulumi/postgresql` provider to declaratively manage PostgreSQL schema and permissions (provider connects to Cloud SQL via Private Service Connect)
- Create `app` schema in Cloud SQL, replacing implicit use of `public`
- Grant `CREATE`, `USAGE`, and default table/sequence privileges to the backend IAM service account on `app`
- Add `DATABASE_SCHEMA` environment variable to backend config (default: `app`), setting `search_path` in the DSN
- Update K8s ConfigMap to set `DATABASE_SCHEMA=app` for all workloads (server, consumer, cronjob)

## Capabilities

### New Capabilities

- `database-schema-management`: Declarative PostgreSQL schema and permission management using Pulumi's postgresql provider

### Modified Capabilities

- `cloud-sql-connector`: Add `search_path` parameter to DSN construction for schema-aware connections
- `database`: Require dedicated schema instead of implicit `public` schema usage

## Impact

- **cloud-provisioning**: New `@pulumi/postgresql` dependency; changes to `src/gcp/components/postgres.ts`; new env var in K8s ConfigMap for all workloads
- **backend**: `DatabaseConfig` struct gains `Schema` field (default: `app`); `GetDSN()` includes `search_path=app,public`; `atlas.hcl` dev URL includes `search_path=app,public`
- **Operations**: `pulumi up` requires the postgresql provider to reach Cloud SQL (managed via PSC endpoint within the VPC)
- **Migration SQL files**: No changes (unqualified table names resolved by `search_path`)
- **Repository queries**: No changes (same reason)
