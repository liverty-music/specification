## Context

The backend consists of three entry points (`cmd/api`, `cmd/consumer`, `cmd/job`) sharing a common DI layer (`internal/di`). All three use `signal.NotifyContext` for SIGTERM handling and a flat `[]io.Closer` slice for resource teardown. The API server runs Connect-RPC on `net/http` with h2c, the consumer runs a Watermill Router over NATS JetStream, and the CronJob executes batch processing then exits.

The application runs on GKE Autopilot where Pod termination involves concurrent SIGTERM delivery and async endpoint removal (2-10s lag). The current implementation has no coordination between these two events, causing dropped requests during rolling deployments.

Key dependencies in the shutdown path: `pgxpool` (database), `cloudsqlconn.Dialer` (PSC), `trace.TracerProvider` (OTel), `watermill/message.Router`, NATS publisher, and several HTTP API clients (LastFM, MusicBrainz, Blockchain RPC).

## Goals / Non-Goals

**Goals:**
- Zero dropped requests during rolling deployments (API server)
- Zero lost events during consumer shutdown (all in-flight handlers complete)
- Correct resource teardown ordering (reverse dependency)
- Health check reflects shutdown state immediately upon SIGTERM
- Timeout budgets aligned between K8s `terminationGracePeriodSeconds` and application shutdown phases
- Leverage Go 1.26 `context.Cause()` for shutdown signal introspection
- All background goroutines tracked and awaited

**Non-Goals:**
- Adding a separate health check HTTP server on a different port (keep using gRPC health on 8080)
- Implementing connection draining at the gRPC/Connect protocol level (rely on `http.Server.Shutdown`)
- Adding startup probes (current `initialDelaySeconds` on readiness probe is sufficient)
- Changing the application's external API contract
- Implementing circuit breakers or retry logic for external clients during shutdown

## Decisions

### D1: Phased Shutdown Manager vs Flat Closer Slice

**Decision**: Introduce a `ShutdownManager` type with named phases in `internal/di/shutdown.go`.

**Alternatives considered**:
- *Keep flat `[]io.Closer`* with reordering — Simple but no per-phase timeout control, no structured logging, no goroutine wait integration.
- *Use `errgroup.Group` directly* — Good for goroutine lifecycle but does not model phases or allow per-closer timeout.

**Rationale**: A `ShutdownManager` provides:
- Named phases (`drain`, `flush`, `external`, `observe`, `datastore`) with per-phase logging
- A single `Execute(ctx)` method that runs phases in order, respecting the parent context deadline
- Integration point for `sync.WaitGroup` (background goroutine drain happens in the `drain` phase)
- Aggregated error collection via `errors.Join`

The manager is lightweight — it wraps `[]io.Closer` into phase groups, not a framework. Each phase is a named slice of `io.Closer`, executed concurrently within the phase and sequentially across phases.

```
type ShutdownManager struct {
    phases []phase
    wg     *sync.WaitGroup    // for background goroutines
    logger *logging.Logger
}

type phase struct {
    name    string
    closers []io.Closer
}
```

### D2: Health Check Shutdown Flag — `atomic.Bool` on Existing Handler

**Decision**: Add `shuttingDown atomic.Bool` field to `HealthCheckHandler`. The `App` struct holds a reference and calls `SetShuttingDown()` at the start of `Shutdown()`, before `Server.Stop()`.

**Alternatives considered**:
- *Context-based check* — Check if a shutdown context is done. But health check runs on the server's request context, not the app context. Threading the app context through is invasive.
- *Channel-based signal* — `select` on a shutdown channel. More Go-idiomatic for some patterns but `atomic.Bool` is simpler for a boolean flag with no blocking.

**Rationale**: `atomic.Bool` is lock-free, zero-allocation, and the simplest primitive for a boolean state transition that only goes `false → true`.

### D3: Consumer Shutdown — Explicit `Router.Close()` with Fresh Context

**Decision**: Restructure `cmd/consumer/main.go` to:
1. Run `Router.Run(ctx)` in a goroutine
2. Wait for `ctx.Done()`
3. Call `Router.Close()` explicitly (which internally waits for in-flight handlers up to `CloseTimeout`)
4. Call `app.Shutdown(context.Background())` with a fresh context

**Alternatives considered**:
- *Keep implicit shutdown via ctx cancellation* — Current approach. `Router.Run(ctx)` internally calls `Close()` when ctx is done. But the caller then also closes resources, risking double-close of the publisher.
- *Use `Router.Running()` channel* — Watermill provides a `Running()` channel to check readiness, but no explicit "fully drained" signal.

**Rationale**: Explicit `Router.Close()` gives us:
- Error reporting on handler timeout
- Guarantee that publishers/subscribers are drained before we close them in the shutdown manager
- Clear separation: Router handles its own lifecycle, then app cleans up infrastructure

### D4: preStop Hook — `sleep 5` vs Custom Script

**Decision**: Use `sleep 5` in preStop exec hook for both server and consumer.

**Alternatives considered**:
- *HTTP endpoint drain check* — More precise but requires a separate health endpoint and scripting in the container.
- *No preStop, rely on readiness probe failure* — Readiness probe period is 10s, so up to 10s of stale routing after SIGTERM. Too slow.

**Rationale**: `sleep 5` is the standard GKE practice. The 5s window covers the typical endpoint propagation time (2-5s for kube-proxy iptables update + GCP NEG sync). Simple, proven, no additional complexity.

### D5: Timeout Budget

**Decision**:

| Component | preStop | App Shutdown | Buffer | Total (terminationGracePeriodSeconds) |
|-----------|---------|-------------|--------|---------------------------------------|
| Server    | 5s      | 45s         | 10s    | 60s                                   |
| Consumer  | 5s      | 60s         | 25s    | 90s                                   |
| CronJob   | 0s      | 90s         | 30s    | 120s                                  |

The consumer gets a longer budget because Watermill handlers may be mid-processing (e.g., DB writes + downstream publishes) and need time to complete.

**App-level `SHUTDOWN_TIMEOUT`**: Change from 30s to 45s for the server, 60s for the consumer. This will be configurable per entry point via environment variable.

### D6: Go 1.26 — `context.Cause()` for Signal Logging

**Decision**: Upgrade `go.mod` to `go 1.26`. Use `context.Cause(ctx)` in the shutdown path to log the exact signal that triggered termination.

```go
<-ctx.Done()
logger.Info(ctx, "shutdown signal received",
    slog.String("cause", context.Cause(ctx).Error()),
)
```

**Rationale**: In Go 1.26, `signal.NotifyContext` cancels the context with `CancelCauseFunc`, attaching the signal as the cause. This replaces the current `ctx.Err().Error()` which only returns "context canceled" — not which signal was received.

### D7: Consumer Health Probes — HTTP Liveness + Readiness

**Decision**: Add a minimal HTTP health server to the consumer on a dedicated port (e.g., 8081) that:
- `/healthz` (liveness): Returns 200 if the process is alive
- `/readyz` (readiness): Returns 200 if `Router.IsRunning()` is true and shutdown flag is not set

**Alternatives considered**:
- *Exec probe with process check* — `pgrep consumer` is brittle and doesn't check functional health.
- *gRPC health like the API server* — Adds Connect-RPC dependency to the consumer, which currently has no HTTP server.

**Rationale**: A lightweight `net/http` server on a separate port is the simplest way to expose health without pulling in the full Connect-RPC stack. The consumer doesn't serve HTTP traffic, so this is probe-only.

## Risks / Trade-offs

**[Risk] preStop `sleep 5` delays every pod termination by 5s** → Acceptable trade-off. Rolling deployments already take time due to `maxUnavailable: 0`. The 5s delay is small relative to pod startup time.

**[Risk] `ShutdownManager` adds abstraction over simple `[]io.Closer`** → Mitigated by keeping it minimal — it's a phase-ordered closer runner, not a framework. If it proves unnecessary, it can be inlined back to a flat list.

**[Risk] Consumer health server port collision** → Use a non-standard port (8081) and document it. GKE Autopilot allows multiple ports per container.

**[Risk] Go 1.26 upgrade may introduce subtle behavior changes** → The Green Tea GC is now default, and crypto packages ignore the `rand` parameter. Neither affects this application. Run full test suite after upgrade.

**[Risk] Watermill `Router.Close()` may hang if a handler is stuck** → The implementation explicitly sets `CloseTimeout: 30s` as a safety net (Watermill's default is `0`, which means wait indefinitely). The consumer's `terminationGracePeriodSeconds: 90` gives enough buffer.
