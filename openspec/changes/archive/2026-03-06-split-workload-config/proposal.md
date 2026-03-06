## Why

The backend uses a single `config.Config` struct loaded by all three workloads (API server, CronJob, consumer). Because `JWTConfig.Issuer` is tagged `required:"true"`, the CronJob and consumer fail at startup if `OIDC_ISSUER_URL` is not set — even though neither workload uses JWT authentication. This surfaced as a blocker during the EDA end-to-end verification (introduce-eda task 9.1). Splitting config by workload ensures each process loads only the environment variables it actually needs, preventing cross-workload configuration leaks.

## What Changes

- Extract a minimal `BaseConfig` struct containing only the fields shared by all workloads: `Environment`, `ShutdownTimeout`, `Logging`, `Database`, `Telemetry`.
- Define `ServerConfig`, `JobConfig`, and `ConsumerConfig` that embed `BaseConfig` and add workload-specific fields (e.g., `JWT`, `Blockchain`, `ZKP` for server; `GCP`, `NATS` for job; `NATS`, `VAPID`, `GoogleMapsAPIKey` for consumer).
- Replace the single `config.Load()` with a generic `config.Load[T]()` function so each DI initializer loads exactly its config type.
- Split `Validate()` into per-type methods: `BaseConfig.Validate()` for shared rules, plus workload-specific validation on each config type.
- Update downstream consumers (`rdb.New`, `telemetry.SetupTelemetry`, `server.NewConnectServer`) to accept narrow field types instead of `*config.Config`.

## Capabilities

### New Capabilities

- `workload-config`: Per-workload configuration loading and validation for the backend.

### Modified Capabilities

(none — this is an internal refactor with no user-facing or API-level behavior changes)

## Impact

- `pkg/config/config.go` — restructure types and load functions
- `pkg/config/config_test.go` — update tests for new types
- `internal/di/provider.go`, `internal/di/job.go`, `internal/di/consumer.go` — use typed Load
- `internal/infrastructure/database/rdb/postgres.go` — narrow signature
- `pkg/telemetry/telemetry.go` — narrow signature
- `internal/infrastructure/server/connect.go` — narrow signature
- No API changes, no database changes, no Protobuf changes
