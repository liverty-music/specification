## 1. Define config types

- [x] 1.1 Rename existing `ServerConfig` (port/host/timeouts/CORS) to `ServerSettings` in `pkg/config/config.go`
- [x] 1.2 Define `BaseConfig` struct with `Environment`, `ShutdownTimeout`, `Logging`, `Database`, `Telemetry`
- [x] 1.3 Move `IsLocal()`, `IsDevelopment()`, `IsStaging()`, `IsProduction()` methods to `BaseConfig`
- [x] 1.4 Define `ServerConfig` embedding `BaseConfig` + `ServerSettings`, `JWT`, `GCP`, `NATS`, `VAPID`, `Blockchain`, `ZKP`, `LastFMAPIKey`
- [x] 1.5 Define `JobConfig` embedding `BaseConfig` + `GCP`, `NATS`
- [x] 1.6 Define `ConsumerConfig` embedding `BaseConfig` + `NATS`, `VAPID`, `GoogleMapsAPIKey`
- [x] 1.7 Remove the old monolithic `Config` struct

## 2. Load and validate functions

- [x] 2.1 Replace `Load()` with generic `Load[T ServerConfig | JobConfig | ConsumerConfig]()` function
- [x] 2.2 Create `BaseConfig.Validate()` with shared checks (environment, DB port, log level/format)
- [x] 2.3 Create `ServerConfig.Validate()` calling base + JWT issuer, CORS (non-local), server port
- [x] 2.4 Create `JobConfig.Validate()` calling base + NATS URL (non-local)
- [x] 2.5 Create `ConsumerConfig.Validate()` calling base + NATS URL (non-local)

## 3. Narrow downstream signatures

- [x] 3.1 Change `rdb.New` to accept `config.DatabaseConfig` + `bool` (isLocal) instead of `*config.Config`
- [x] 3.2 Change `telemetry.SetupTelemetry` to accept `config.TelemetryConfig` + `time.Duration` instead of `*config.Config`
- [x] 3.3 Change `server.NewConnectServer` to accept `config.ServerSettings` instead of `*config.Config`
- [x] 3.4 Change `provideLogger` to accept `config.LoggingConfig` instead of `*config.Config`

## 4. Update DI initializers

- [x] 4.1 Update `InitializeApp` in `internal/di/provider.go` to use `config.Load[config.ServerConfig]()`
- [x] 4.2 Update `InitializeJobApp` in `internal/di/job.go` to use `config.Load[config.JobConfig]()`
- [x] 4.3 Update `InitializeConsumerApp` in `internal/di/consumer.go` to use `config.Load[config.ConsumerConfig]()`

## 5. Update tests

- [x] 5.1 Update `pkg/config/config_test.go` for new types, `Load[T]()`, and per-type `Validate()`
- [x] 5.2 Update any integration tests that reference `config.Config` or `config.Load()`
- [x] 5.3 Run `make check` in backend to verify all tests pass

## 6. Verify in cluster

- [ ] 6.1 Create a manual Job from CronJob and verify it starts successfully without `OIDC_ISSUER_URL`
