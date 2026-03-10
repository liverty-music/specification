## Context

The Go backend connects to Cloud SQL via `pgxpool` with the Cloud SQL Go Connector (IAM authentication over PSC). The connection pool is configured in two places:

- **Config defaults**: `backend/pkg/config/config.go` — `DatabaseConfig` struct with `envconfig` tags
- **Pool creation**: `backend/internal/infrastructure/database/rdb/postgres.go` — applies config to `pgxpool.Config`

Current state:
- `MaxConns=25` (matches entire `db-f1-micro` capacity for a single pod)
- `MinConns=5` (applied)
- `ConnMaxLifetime=300s` (defined in config but **never applied** to pgxpool — pgxpool default of 1h is used instead)
- `MaxConnIdleTime` — not configured (pgxpool default: 30min)
- `HealthCheckPeriod` — not configured (pgxpool default: 1min)

Dev environment (`db-f1-micro`, `max_connections=25`) runs three workloads:
- `server-app` (1 pod)
- `consumer-app` (1 pod)
- `concert-discovery` CronJob (periodic)
- Atlas Operator (on-demand, 1-2 connections)

None of the dev overlay ConfigMaps set `DATABASE_MAX_OPEN_CONNS` or related pool env vars.

## Goals / Non-Goals

**Goals:**
- Fix the `ConnMaxLifetime` bug (config value not applied to pgxpool)
- Set safe default pool sizes that work across environments
- Add `MaxConnIdleTime` and `HealthCheckPeriod` as configurable settings
- Override pool sizes in dev overlay to fit `db-f1-micro` connection budget
- Document the rationale for each setting value with inline code comments

**Non-Goals:**
- Changing the Cloud SQL instance tier (stays `db-f1-micro` for dev cost optimization)
- Increasing `max_connections` on the DB side
- Adding connection pool metrics/observability (future work)
- Configuring `ConnConfig.ConnectTimeout` (pgx DSN-level; separate concern)

## Decisions

### 1. Default pool sizes: `MaxOpenConns=10`, `MaxIdleConns=2`

**Rationale**: The previous default of 25 matched the entire DB capacity of `db-f1-micro`. A default of 10 is safe for most environments while leaving headroom for multiple pods and operational connections. `MaxIdleConns=2` keeps a small warm pool without wasting DB slots.

**Alternative considered**: Default of 5 — too conservative for production workloads with higher connection counts. The dev overlay will set 5 explicitly.

### 2. `ConnMaxLifetime` default: 1800s (30 minutes)

**Rationale**: The previous config default of 300s (5min) was never applied (bug), but 5 minutes is also too aggressive — it causes ~60 reconnections/hour/pod through the Cloud SQL Connector (PSC + TLS + IAM), adding unnecessary overhead. 30 minutes balances connection freshness with reconnection cost.

IAM token consideration: PostgreSQL authenticates only at connection establishment. The Cloud SQL Go Connector auto-refreshes tokens internally for new connections. So `MaxConnLifetime` does not need to be shorter than the 60-minute token lifetime for auth safety. However, keeping it well under 60 minutes ensures connections are recycled regularly for general hygiene (server-side memory, Cloud SQL maintenance).

**Alternative considered**: 45 minutes — also reasonable, but 30 minutes is a more commonly recommended value in Cloud SQL documentation.

### 3. Add `MaxConnIdleTime` with default 600s (10 minutes)

**Rationale**: pgxpool's default is 30 minutes. In resource-constrained environments like `db-f1-micro`, idle connections beyond `MinConns` should be released sooner to free DB connection slots for other workloads. 10 minutes provides a reasonable idle timeout while avoiding excessive churn during brief traffic lulls.

### 4. Add `HealthCheckPeriod` with default 60s (1 minute)

**Rationale**: This matches pgxpool's default. Making it explicit and configurable serves two purposes: (1) documents the intent — pool periodically validates idle connections to detect stale connections from Cloud SQL restarts or network interruptions, and (2) allows per-environment tuning via env vars if needed.

### 5. Dev overlay connection budget

```
db-f1-micro max_connections = 25

┌───────────────────────┬───────┐
│ Workload              │ Conns │
├───────────────────────┼───────┤
│ server-app (1 pod)    │     5 │
│ consumer-app (1 pod)  │     5 │
│ concert-discovery job │     5 │  ← shares time with other workloads
│ Atlas Operator        │   1-2 │
│ Reserved / headroom   │  8-9  │
├───────────────────────┼───────┤
│ Total                 │   ≤25 │
└───────────────────────┴───────┘
```

Set `DATABASE_MAX_OPEN_CONNS=5` and `DATABASE_MAX_IDLE_CONNS=1` in all three dev overlay ConfigMaps (server, consumer, cronjob).

### 6. Inline comments for all pool settings

Each setting in `postgres.go` will have a comment explaining:
- What the setting controls
- Why the value was chosen
- Relationship to other settings or constraints (e.g., Cloud SQL IAM auth, `db-f1-micro` limits)

## Risks / Trade-offs

- **[Lower defaults may be insufficient for future prod scaling]** → Mitigated by env var overrides per environment. Production overlays can set higher values as needed.
- **[Dev overlay hardcodes connection budget]** → Acceptable for dev tier. If workloads scale, the overlay values are easy to update.
- **[CronJob shares the connection budget]** → The concert-discovery job runs periodically and doesn't overlap continuously with server/consumer. The budget has 8-9 slots of headroom.
