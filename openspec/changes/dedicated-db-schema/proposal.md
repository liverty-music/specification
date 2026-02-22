## Why

The dev Cloud SQL (PostgreSQL 18) denies `CREATE` on the `public` schema to IAM-authenticated users, blocking goose migrations. PostgreSQL 15+ revokes default `CREATE` privileges on `public` from non-superusers. The database has no tables yet, making this the ideal time to adopt a dedicated `liverty_music` schema instead of patching `public` permissions.

## What Changes

- Introduce Pulumi `@pulumi/postgresql` provider to declaratively manage PostgreSQL schema and permissions via Cloud SQL Auth Proxy
- Create `liverty_music` schema in Cloud SQL, replacing implicit use of `public`
- Grant `CREATE`, `USAGE`, and default table/sequence privileges to the backend IAM service account on `liverty_music`
- Add `DATABASE_SCHEMA` environment variable to backend config, setting `search_path` in the DSN
- Update K8s ConfigMap to set `DATABASE_SCHEMA=liverty_music` for dev environment

## Capabilities

### New Capabilities

- `database-schema-management`: Declarative PostgreSQL schema and permission management using Pulumi's postgresql provider

### Modified Capabilities

- `cloud-sql-connector`: Add `search_path` parameter to DSN construction for schema-aware connections
- `database`: Require dedicated schema instead of implicit `public` schema usage

## Impact

- **cloud-provisioning**: New `@pulumi/postgresql` dependency; changes to `src/gcp/components/postgres.ts`; new env var in K8s ConfigMap
- **backend**: `DatabaseConfig` struct gains `Schema` field; `GetDSN()` includes `search_path`; `atlas.hcl` dev URL updated
- **Operations**: `pulumi up` requires Cloud SQL Auth Proxy running locally for postgresql provider connectivity
- **Migration SQL files**: No changes (unqualified table names resolved by `search_path`)
- **Repository queries**: No changes (same reason)
