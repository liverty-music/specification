## Context

The backend has three workloads sharing a single `config.Config` struct:

| Workload   | Entry point                        | Purpose                        |
|------------|------------------------------------|--------------------------------|
| **Server** | `cmd/server/main.go`               | Connect-RPC API server         |
| **Job**    | `cmd/job/concert-discovery/main.go`| Batch concert discovery CronJob|
| **Consumer**| `cmd/consumer/main.go`            | Watermill event consumer       |

All three call `config.Load()` → `envconfig.Process("", &Config{})`, which requires every `required:"true"` field to be set regardless of whether the workload uses it. This causes startup failures when workload-specific env vars are absent.

Actual field usage per workload (verified from DI code):

```
Field               Server  Job     Consumer
Environment         x       x       x
ShutdownTimeout     x       x       x
Logging             x       x       x
Database            x       x       x
Telemetry           x       x       x
GCP                 x       x       -
NATS                x       x       x
VAPID               x       -       x
LastFMAPIKey        x       -       -
GoogleMapsAPIKey    -       -       x
Server (port etc)   x       -       -
JWT                 x       -       -
Blockchain          x       -       -
ZKP                 x       -       -
```

Downstream functions that currently accept `*config.Config` but only use subsets:
- `rdb.New` → uses `cfg.Database` + `cfg.IsLocal()`
- `telemetry.SetupTelemetry` → uses `cfg.Telemetry` + `cfg.ShutdownTimeout`
- `server.NewConnectServer` → uses `cfg.Server`

## Goals / Non-Goals

**Goals:**
- Each workload loads only the environment variables it needs
- `required:"true"` tags on workload-specific fields do not affect other workloads
- Downstream functions accept narrow types instead of the full config struct
- Adding a new workload requires defining its config type explicitly

**Non-Goals:**
- Changing environment variable names (all env var names remain identical)
- Modifying ConfigMap/Secret manifests (they already contain only what each workload needs)
- Introducing a config file format (stay with envconfig)

## Decisions

### 1. Embed-based config composition

Define a `BaseConfig` with fields used by all three workloads, then compose workload-specific configs via struct embedding.

```go
type BaseConfig struct {
    Environment     string        `envconfig:"ENVIRONMENT" default:"local"`
    ShutdownTimeout time.Duration `envconfig:"SHUTDOWN_TIMEOUT" default:"30s"`
    Logging         LoggingConfig
    Database        DatabaseConfig
    Telemetry       TelemetryConfig
}

type ServerConfig struct {
    BaseConfig
    Server          ServerSettings
    JWT             JWTConfig
    GCP             GCPConfig
    NATS            NATSConfig
    VAPID           VAPIDConfig
    Blockchain      BlockchainConfig
    ZKP             ZKPConfig
    LastFMAPIKey    string `envconfig:"LASTFM_API_KEY"`
}

type JobConfig struct {
    BaseConfig
    GCP  GCPConfig
    NATS NATSConfig
}

type ConsumerConfig struct {
    BaseConfig
    NATS             NATSConfig
    VAPID            VAPIDConfig
    GoogleMapsAPIKey string `envconfig:"GOOGLE_MAPS_API_KEY"`
}
```

**Why embed over interface**: `kelseyhightower/envconfig` flattens embedded structs during `Process()`. No wrapper code needed — embedding just works. An interface-based approach would require manual field delegation.

**Why NATS is not in BaseConfig**: Future workloads (e.g., migration tools, admin CLIs) may not need messaging. NATS is infrastructure for event-driven workloads, not a universal requirement.

### 2. Generic `Load[T]` function

```go
type Loadable interface {
    ServerConfig | JobConfig | ConsumerConfig
}

func Load[T Loadable]() (*T, error) {
    var cfg T
    if err := envconfig.Process("", &cfg); err != nil {
        return nil, fmt.Errorf("failed to load configuration: %w", err)
    }
    return &cfg, nil
}
```

**Why generic over separate functions**: Avoids three nearly-identical `LoadServer/LoadJob/LoadConsumer` functions. The type constraint documents which config types are valid. Adding a new workload means adding its type to the union constraint.

### 3. Per-type `Validate()` with shared base

```go
func (c *BaseConfig) Validate() error {
    // Environment, DB port, log level/format checks
}

func (c *ServerConfig) Validate() error {
    if err := c.BaseConfig.Validate(); err != nil { return err }
    // JWT issuer required, CORS required (non-local), server port range
}

func (c *JobConfig) Validate() error {
    if err := c.BaseConfig.Validate(); err != nil { return err }
    // NATS URL required (non-local)
}

func (c *ConsumerConfig) Validate() error {
    if err := c.BaseConfig.Validate(); err != nil { return err }
    // NATS URL required (non-local)
}
```

Validation rules that currently exist in the monolithic `Validate()` are distributed to the appropriate type. Server-only checks (JWT, CORS) move to `ServerConfig.Validate()`.

### 4. Narrow downstream function signatures

| Function | Current | New |
|----------|---------|-----|
| `rdb.New` | `*config.Config` | `config.DatabaseConfig, bool` (isLocal) |
| `telemetry.SetupTelemetry` | `*config.Config` | `config.TelemetryConfig, time.Duration` (shutdownTimeout) |
| `server.NewConnectServer` | `*config.Config` | `config.ServerSettings` |
| `provideLogger` | `*config.Config` | `config.LoggingConfig` |

This eliminates the coupling between infrastructure packages and the full config struct.

### 5. Rename `ServerConfig` (port/host) to `ServerSettings`

The existing `ServerConfig` struct (port, host, timeouts, CORS) conflicts with the new top-level `ServerConfig` (the full server workload config). Rename the inner struct to `ServerSettings` to avoid ambiguity.

### 6. Environment helper methods on BaseConfig

`IsLocal()`, `IsDevelopment()`, etc. move from `Config` to `BaseConfig`, making them available to all workload config types via embedding.

## Risks / Trade-offs

**[Duplication of NATS/VAPID/GCP across config types]** → Acceptable trade-off. Each field appears in exactly the types that use it. The alternative (putting everything in BaseConfig) is what caused the original bug.

**[envconfig embedding behavior]** → `kelseyhightower/envconfig` v1.4.0 supports embedded structs natively by flattening fields. Verified in the library source. No risk here.

**[Breaking `provideLogger` and infrastructure function signatures]** → All callers are internal (`internal/di/`). No external consumers. The change is safe to make in one PR.
