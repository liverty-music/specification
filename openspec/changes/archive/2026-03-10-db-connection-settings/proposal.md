## Why

The Go app's default `MaxOpenConns` (25 per pod) equals the entire `max_connections` limit of the Cloud SQL `db-f1-micro` instance. With multiple pods (`server-app` + `consumer-app` + Atlas Operator), total connection demand (~52) far exceeds the 25 available slots, causing `FATAL: remaining connection slots are reserved` errors. Additionally, `ConnMaxLifetime` is defined in config but never applied to the pgxpool, and `MaxConnIdleTime` is not configured at all — both are important for connection hygiene in a Cloud SQL IAM-authenticated environment.

Ref: https://github.com/liverty-music/backend/issues/173

## What Changes

- Lower `MaxOpenConns` default from 25 to 10 and `MaxIdleConns` from 5 to 2 for safer per-pod connection budgeting
- Fix `ConnMaxLifetime` bug: value is defined in config but never applied to pgxpool; change default from 300s to 1800s (30min)
- Add `MaxConnIdleTime` setting (default: 600s / 10min) to release idle connections beyond MinConns promptly
- Add `HealthCheckPeriod` setting (default: 60s / 1min, matching pgxpool default) for explicit intent
- Add dev overlay environment variables (`DATABASE_MAX_OPEN_CONNS=5`, `DATABASE_MAX_IDLE_CONNS=2`) to fit `db-f1-micro` connection budget
- Add inline comments explaining the rationale for each connection pool setting value
- Add `ConnMaxLifetime` to the connection-established log output

## Capabilities

### New Capabilities

None — this is an infrastructure configuration fix, not a new feature.

### Modified Capabilities

None — no spec-level behavior changes.

## Impact

- **backend** `pkg/config/config.go`: New config fields, updated defaults
- **backend** `internal/infrastructure/database/rdb/postgres.go`: Apply all pool settings to pgxpool, add comments explaining each value
- **cloud-provisioning** `k8s/namespaces/backend/overlays/dev/`: Add connection pool env vars to ConfigMap
