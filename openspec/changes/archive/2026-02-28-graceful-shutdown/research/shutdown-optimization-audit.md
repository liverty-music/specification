# Audit: Shutdown Package Optimization Opportunities

**Date**: 2026-02-28
**Scope**: Maximizing `pkg/shutdown` usage across all entry points
**Status**: Implemented

---

## 1. Audit Summary

After implementing the five-phase `pkg/shutdown` package (drain → flush → external → observe → datastore), an audit identified that three components still had manual shutdown logic in `App.Shutdown()` methods rather than being registered with the shutdown package. This created unnecessary coupling between DI structs and shutdown orchestration.

### Components Audited

| Component | Phase | Was Registered? | Manual Logic? |
|-----------|-------|----------------|---------------|
| `MemoryCache` | drain | YES | No |
| `Publisher` (NATS/GoChannel) | flush | YES | No |
| `LastFM Client` | external | YES | No |
| `MusicBrainz Client` | external | YES | No |
| `Blockchain SBT Client` | external | YES | No |
| `Telemetry Closer` | observe | YES | No |
| `Database Pool` | datastore | YES | No |
| **`ConnectServer`** | drain | **NO** | **YES** — `App.Shutdown()` called `Server.Stop()` |
| **`HealthCheckHandler`** | drain | **NO** | **YES** — `App.Shutdown()` called `SetShuttingDown()` |
| **`HealthServer`** | drain | **NO** | **YES** — `ConsumerApp.Shutdown()` called `SetShuttingDown()` + `Shutdown()` |
| **`Watermill Router`** | drain | **NO** | **YES** — `cmd/consumer/main.go` called `Router.Close()` |

---

## 2. Issues Found

### 2.1 App.Shutdown() Methods Were Redundant Wrappers

All three App structs (`App`, `ConsumerApp`, `JobApp`) had `Shutdown(ctx)` methods that:
1. Performed manual pre-shutdown steps (health transition, server stop)
2. Called `shutdown.Shutdown(ctx)` for the phased teardown

This split shutdown into two stages: "manual stuff first, then phases". The manual steps should have been registered as Drain phase closers.

**Impact**: Fragile ordering. If someone added a new resource but forgot to update `App.Shutdown()`, the resource would be skipped.

### 2.2 ConnectServer Did Not Implement io.Closer

`ConnectServer` had a `Stop()` method but not `Close()`. This meant it could not be registered with the shutdown package, which requires `io.Closer`.

**Fix**: Renamed `Stop()` → `Close()` to implement `io.Closer`. The method internally calls `http.Server.Shutdown(ctx)` with the configured timeout.

### 2.3 HealthServer Required Manual Two-Step Shutdown

`HealthServer` had separate `SetShuttingDown()` and `Shutdown(ctx)` methods. The consumer's `ConsumerApp.Shutdown()` had to call both in sequence. This forced every entry point to know the internal protocol.

**Fix**: Added `Close()` method that combines `SetShuttingDown()` + `srv.Shutdown(context.Background())`. Registered in Drain phase.

### 2.4 HealthCheckHandler (gRPC Health) Not in Shutdown Flow

The API server's `HealthCheckHandler` had `SetShuttingDown()` called from `App.Shutdown()`. It was not registered with the shutdown package.

**Fix**: Added `Close()` method that delegates to `SetShuttingDown()`. Registered in Drain phase before `ConnectServer`.

### 2.5 Watermill Router Manually Closed in Entry Point

`cmd/consumer/main.go` had explicit `app.Router.Close()` in the signal handler, separate from the shutdown package flow. The router already implements `io.Closer`.

**Fix**: Registered `router` in Drain phase in `consumer.go` initialization. Removed manual `Router.Close()` from entry point.

### 2.6 JobApp.Shutdown() Was a Pure Pass-Through

`JobApp.Shutdown()` only logged and called `shutdown.Shutdown(ctx)`. No pre-shutdown steps. Pure overhead.

**Fix**: Eliminated entirely. Entry point calls `shutdown.Shutdown()` directly.

---

## 3. Architecture After Optimization

### 3.1 Simplified App Structs

```
BEFORE                                    AFTER
──────                                    ─────
type App struct {                         type App struct {
    Server        *ConnectServer              Server *ConnectServer
    Logger        *logging.Logger             Logger *logging.Logger
    healthHandler *HealthCheckHandler     }
}
func (a *App) Shutdown(ctx) error { ... }  // REMOVED
```

All three App structs are now pure data holders — no lifecycle methods.

### 3.2 Unified Shutdown Flow

```
cmd/api/main.go                     cmd/consumer/main.go
       │                                   │
  shutdown.Shutdown(ctx)             shutdown.Shutdown(ctx)
       │                                   │
       ▼                                   ▼
  ┌──────────────────────────────────────────────────┐
  │                pkg/shutdown                       │
  │                                                   │
  │  Phase 1 (drain):                                │
  │    API: healthChecker → ConnectServer → cache    │
  │    Consumer: healthServer → router               │
  │                                                   │
  │  Phase 2 (flush):  publisher                     │
  │  Phase 3 (external): lastfm, musicbrainz, [sbt] │
  │  Phase 4 (observe): telemetry                    │
  │  Phase 5 (datastore): database                   │
  └──────────────────────────────────────────────────┘
```

### 3.3 Entry Point Simplification

```go
// BEFORE: Each entry point called app-specific Shutdown method
defer func() {
    if err := app.Shutdown(context.Background()); err != nil { ... }
}()

// AFTER: All entry points call the same package function
defer func() {
    if err := shutdown.Shutdown(context.Background()); err != nil { ... }
}()
```

### 3.4 Resource Registration Completeness

After optimization, ALL closeable resources are registered with `pkg/shutdown`:

| Phase | API Server | Consumer | CronJob |
|-------|-----------|----------|---------|
| drain | healthChecker, connectServer, cache | healthServer, router | — |
| flush | publisher | publisher | publisher |
| external | lastfm, musicbrainz, [sbt] | musicbrainz | — |
| observe | telemetry | telemetry | telemetry |
| datastore | database | database | database |

---

## 4. Key Design Decisions

### 4.1 Drain Phase Closer Ordering

Within a phase, closers run **concurrently**. For the API server's Drain phase, `healthChecker`, `connectServer`, and `cache` all close concurrently. This is safe because:

- `healthChecker.Close()` is atomic (`atomic.Bool.Store(true)`) — no dependencies
- `connectServer.Close()` calls `http.Server.Shutdown()` which drains in-flight requests — independent of cache
- `cache.Close()` stops the cleanup ticker — independent of server

For the consumer's Drain phase, `healthServer` and `router` closing concurrently is safe because they serve independent concerns (HTTP health probes vs NATS message handlers).

### 4.2 io.Closer as Universal Contract

All resources use `io.Closer` as the shutdown contract. This provides:
- Compile-time verification of the interface
- Zero runtime type assertions
- Standard library compatibility
- Easy mock/stub in tests

### 4.3 No Per-Phase Timeouts

Individual phases do not have timeouts. The overall shutdown timeout is enforced by the context deadline passed to `shutdown.Shutdown(ctx)`. If finer-grained timeout control is needed in the future, `ConnectServer.Close()` already uses its own `cfg.ShutdownTimeout` internally.

---

## 5. Verification

- `go build ./...` — compiles cleanly
- `go test ./pkg/shutdown/...` — 10 tests, all pass
- `go test ./internal/adapter/rpc/...` — health handler tests pass
- No remaining `app.Shutdown()` calls in codebase
- No remaining manual `Router.Close()` or `Server.Stop()` calls
