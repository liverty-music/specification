## ADDED Requirements

### Requirement: Workload-specific configuration loading

The system SHALL define separate configuration types for each backend workload (server, job, consumer). Each type SHALL contain only the environment variables that the workload actually references. A shared `BaseConfig` type SHALL contain fields common to all workloads: `Environment`, `ShutdownTimeout`, `Logging`, `Database`, and `Telemetry`. Workload-specific types SHALL embed `BaseConfig` and add their own fields.

#### Scenario: CronJob starts without OIDC_ISSUER_URL
- **WHEN** the concert-discovery CronJob starts and `OIDC_ISSUER_URL` is not set
- **THEN** configuration loading SHALL succeed because `JobConfig` does not include JWT fields

#### Scenario: Consumer starts without JWT or Blockchain config
- **WHEN** the event consumer starts and `OIDC_ISSUER_URL`, `BASE_SEPOLIA_RPC_URL`, `ZKP_VERIFICATION_KEY_PATH` are not set
- **THEN** configuration loading SHALL succeed because `ConsumerConfig` does not include JWT, Blockchain, or ZKP fields

#### Scenario: Server requires OIDC_ISSUER_URL
- **WHEN** the API server starts and `OIDC_ISSUER_URL` is not set
- **THEN** configuration loading SHALL fail with a clear error indicating the missing field

### Requirement: Generic configuration load function

The system SHALL provide a generic `Load[T]()` function that loads environment variables into the specified configuration type. The type parameter SHALL be constrained to valid workload configuration types.

#### Scenario: Load ServerConfig
- **WHEN** `Load[ServerConfig]()` is called with all server environment variables set
- **THEN** the function SHALL return a fully populated `*ServerConfig` with all embedded `BaseConfig` fields resolved

#### Scenario: Load JobConfig
- **WHEN** `Load[JobConfig]()` is called with only base + job-specific environment variables set
- **THEN** the function SHALL return a fully populated `*JobConfig` without requiring server-specific variables

### Requirement: Per-type validation

Each workload configuration type SHALL implement a `Validate()` method. `BaseConfig.Validate()` SHALL check shared constraints (environment value, database port range, log level, log format). Workload-specific `Validate()` methods SHALL call `BaseConfig.Validate()` first, then check their own constraints.

#### Scenario: ServerConfig validation enforces JWT
- **WHEN** `ServerConfig.Validate()` is called and `JWT.Issuer` is empty
- **THEN** validation SHALL return an error indicating JWT issuer is required

#### Scenario: JobConfig validation does not check JWT
- **WHEN** `JobConfig.Validate()` is called
- **THEN** validation SHALL NOT check for JWT, Blockchain, ZKP, or Server fields

#### Scenario: NATS URL required in non-local environments
- **WHEN** `JobConfig.Validate()` or `ConsumerConfig.Validate()` is called with `Environment` not equal to `"local"` and `NATS.URL` is empty
- **THEN** validation SHALL return an error indicating NATS URL is required

### Requirement: Narrow downstream function signatures

Infrastructure functions that accept `*config.Config` SHALL be refactored to accept only the fields they use. This eliminates coupling between infrastructure packages and the full configuration struct.

#### Scenario: Database initialization accepts DatabaseConfig
- **WHEN** `rdb.New` is called
- **THEN** it SHALL accept `config.DatabaseConfig` and a `bool` indicating local environment, not the full config struct

#### Scenario: Telemetry setup accepts TelemetryConfig
- **WHEN** `telemetry.SetupTelemetry` is called
- **THEN** it SHALL accept `config.TelemetryConfig` and a `time.Duration` for shutdown timeout, not the full config struct

#### Scenario: Connect server accepts ServerSettings
- **WHEN** `server.NewConnectServer` is called
- **THEN** it SHALL accept `config.ServerSettings` (renamed from `ServerConfig`), not the full config struct
