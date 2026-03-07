## Context

The dev Cloud SQL instance (PostgreSQL 18) denies `CREATE` on the `public` schema to IAM-authenticated users. This is expected behavior in PostgreSQL 15+. The database had no tables, making this the ideal time to adopt a dedicated schema.

Current state (before this change):
- 35 migration SQL files use unqualified table names (e.g., `CREATE TABLE users`, not `CREATE TABLE public.users`)
- DSN did not set `search_path` (relied on PostgreSQL default `"$user",public`)
- All repository queries use unqualified table names
- No `DatabaseConfig.Schema` field existed

## Goals / Non-Goals

**Goals:**
- Create `app` schema in Cloud SQL managed declaratively by Pulumi
- Grant IAM SA permissions on the schema via Pulumi
- Route all backend queries to `app` via `search_path` DSN parameter
- Zero changes to migration SQL files or repository queries

**Non-Goals:**
- Migrating existing data (no tables existed)
- Multi-schema architecture or schema-per-tenant
- Changing table names or adding schema qualification to queries

## Decisions

### Decision 1: Pulumi `@pulumi/postgresql` provider for schema management

**Choice**: Use `@pulumi/postgresql` provider to create schema and manage grants declaratively.

**Why**: The project's policy is to manage infrastructure resources via Pulumi. The postgresql provider supports `Schema`, `Grant`, and `DefaultPrivileges` resources. It connects to Cloud SQL via the PSC endpoint within the VPC during `pulumi up`.

**Alternatives considered**:
- Atlas migration: Cannot `CREATE SCHEMA` with IAM SA user (needs superuser). Also mixes infrastructure concerns with application migrations.
- Manual SQL: Not IaC, not reproducible across environments.

### Decision 2: `search_path` in DSN instead of schema-qualified queries

**Choice**: Set `search_path=app,public` in the DSN connection string.

**Why**: All migration files and all repository queries use unqualified table names. Setting `search_path` makes PostgreSQL resolve unqualified names to `app` without any code changes. This is the standard PostgreSQL approach.

### Decision 3: `DATABASE_SCHEMA` env var with `app` default

**Choice**: Add `DATABASE_SCHEMA` env var (default: `app`) to `DatabaseConfig`.

**Why**: All environments (local, dev, staging, prod) use the `app` schema consistently. Local development uses the same schema name via `atlas.hcl` dev URL (`search_path=app,public`).

### Decision 4: PostgreSQL provider connects via Private Service Connect

**Choice**: The `@pulumi/postgresql` provider connects to Cloud SQL through the PSC endpoint within the VPC.

**Why**: Cloud SQL is configured with Private Service Connect (PSC). The PSC endpoint provides a stable internal IP (`10.10.10.10`) with private DNS resolution via `asia-northeast2.sql.goog.`. The provider uses the `postgres` superuser credentials to manage schema and grants. No Cloud SQL Auth Proxy is involved.

## Risks / Trade-offs

- **[Risk] Provider uses `postgres` superuser** → This is the Cloud SQL default admin user. IAM SA cannot create schemas. The `postgres` user is only used by Pulumi, not by the application.
- **[Risk] PSC connectivity required for `pulumi up`** → The Pulumi postgresql provider must be able to reach Cloud SQL via PSC. This means `pulumi up` must run from a context that can reach the VPC (e.g., CI/CD within GCP, or via VPN).
- **[Trade-off] Schema name `app` is generic** → Chosen for brevity and simplicity. Acceptable since this is a single-service database with no multi-tenant requirements.

## Open Questions

None — implementation is complete.
