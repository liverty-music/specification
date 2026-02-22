## Context

The dev Cloud SQL instance (PostgreSQL 18) denies `CREATE` on the `public` schema to IAM-authenticated users. This is expected behavior in PostgreSQL 15+. The database currently has no tables, making this the ideal time to adopt a dedicated schema.

Current state:
- 17 migration SQL files use unqualified table names (e.g., `CREATE TABLE users`, not `CREATE TABLE public.users`)
- DSN does not set `search_path` (relies on PostgreSQL default `"$user",public`)
- All repository queries use unqualified table names
- No `DatabaseConfig.Schema` field exists

## Goals / Non-Goals

**Goals:**
- Create `liverty_music` schema in Cloud SQL managed declaratively by Pulumi
- Grant IAM SA permissions on the schema via Pulumi
- Route all backend queries to `liverty_music` via `search_path` DSN parameter
- Zero changes to migration SQL files or repository queries

**Non-Goals:**
- Migrating existing data (no tables exist yet)
- Multi-schema architecture or schema-per-tenant
- Changing table names or adding schema qualification to queries

## Decisions

### Decision 1: Pulumi `@pulumi/postgresql` provider for schema management

**Choice**: Use `@pulumi/postgresql` provider to create schema and manage grants declaratively.

**Why**: The user's policy is to manage infrastructure resources via Pulumi. The postgresql provider supports `Schema`, `Grant`, and `DefaultPrivileges` resources. It connects to Cloud SQL via Cloud SQL Auth Proxy running locally during `pulumi up`.

**Alternatives considered**:
- goose migration: Cannot `CREATE SCHEMA` with IAM SA user (needs superuser). Also mixes infrastructure concerns with application migrations.
- Manual SQL: Not IaC, not reproducible across environments.

### Decision 2: `search_path` in DSN instead of schema-qualified queries

**Choice**: Set `search_path=liverty_music` in the DSN connection string.

**Why**: All 17 migration files and all repository queries use unqualified table names. Setting `search_path` makes PostgreSQL resolve unqualified names to `liverty_music` without any code changes. This is the standard PostgreSQL approach.

### Decision 3: `DATABASE_SCHEMA` env var with `public` default

**Choice**: Add `DATABASE_SCHEMA` env var (default: `public`) to `DatabaseConfig`.

**Why**: Local development can continue using `public` schema (PostgreSQL default behavior preserved). Only Cloud SQL environments set `DATABASE_SCHEMA=liverty_music` via K8s ConfigMap.

### Decision 4: PostgreSQL provider connects via Cloud SQL Auth Proxy

**Choice**: The `@pulumi/postgresql` provider connects to `localhost:5432` via Cloud SQL Auth Proxy.

**Why**: Cloud SQL only allows Private Service Connect or Auth Proxy connections. Auth Proxy is the standard local access method. The proxy handles IAM authentication and TLS.

**Prerequisite**: `cloud-sql-proxy liverty-music-dev:asia-northeast2:postgres-osaka --port 5432` must be running before `pulumi up`.

## Risks / Trade-offs

- **[Risk] Auth Proxy dependency for `pulumi up`** → Document the prerequisite. Add a check or clear error message if provider can't connect.
- **[Risk] Provider uses `postgres` superuser** → This is the Cloud SQL default admin user. IAM SA cannot create schemas. The `postgres` user is only used by Pulumi, not by the application.
- **[Trade-off] Local dev still uses `public`** → Acceptable. Local PostgreSQL (docker) allows `CREATE` on `public`. Setting up a `liverty_music` schema locally would add complexity without benefit.

## Open Questions

None — approach is clear from the exploration session.
