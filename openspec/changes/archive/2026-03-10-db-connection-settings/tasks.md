## 1. Backend: Config defaults and new fields

- [x] 1.1 Update `MaxOpenConns` default from `25` to `10` in `pkg/config/config.go`
- [x] 1.2 Update `MaxIdleConns` default from `5` to `2` in `pkg/config/config.go`
- [x] 1.3 Update `ConnMaxLifetime` default from `300` to `1800` in `pkg/config/config.go`
- [x] 1.4 Add `MaxConnIdleTime` field (env: `DATABASE_MAX_CONN_IDLE_TIME`, default: `600`) to `DatabaseConfig`
- [x] 1.5 Add `HealthCheckPeriod` field (env: `DATABASE_HEALTH_CHECK_PERIOD`, default: `60`) to `DatabaseConfig`

## 2. Backend: Apply all pool settings to pgxpool

- [x] 2.1 Apply `MaxConnLifetime` from `dbCfg.ConnMaxLifetime` to `poolConfig.MaxConnLifetime` in `postgres.go`
- [x] 2.2 Apply `MaxConnIdleTime` from `dbCfg.MaxConnIdleTime` to `poolConfig.MaxConnIdleTime` in `postgres.go`
- [x] 2.3 Apply `HealthCheckPeriod` from `dbCfg.HealthCheckPeriod` to `poolConfig.HealthCheckPeriod` in `postgres.go`
- [x] 2.4 Add inline comments to each pool setting explaining its purpose and rationale for the chosen default value
- [x] 2.5 Add `ConnMaxLifetime`, `MaxConnIdleTime`, and `HealthCheckPeriod` to the connection-established log output

## 3. Cloud Provisioning: Dev overlay connection budget

- [x] 3.1 Add `DATABASE_MAX_OPEN_CONNS=5` and `DATABASE_MAX_IDLE_CONNS=1` to `server/configmap.env`
- [x] 3.2 Add `DATABASE_MAX_OPEN_CONNS=5` and `DATABASE_MAX_IDLE_CONNS=1` to `consumer/configmap.env`
- [x] 3.3 Add `DATABASE_MAX_OPEN_CONNS=5` and `DATABASE_MAX_IDLE_CONNS=1` to `cronjob/concert-discovery/configmap.env`

## 4. Verification

- [x] 4.1 Run `make check` in the backend repo to verify lint and tests pass
- [x] 4.2 Run `make check` in the cloud-provisioning repo to verify kustomize render and lint pass
