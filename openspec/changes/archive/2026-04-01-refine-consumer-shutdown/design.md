## Context

The backend has four entry points sharing a common `pkg/shutdown` package that orchestrates five-phase teardown (Drain → Flush → External → Observe → Datastore). The API server is well-integrated: its `ConnectServer` is registered in Drain phase, ensuring in-flight requests complete before downstream resources close.

The consumer and CronJob entry points have gaps in this integration, identified through code analysis:

1. **Consumer**: Watermill `Router.Run(ctx)` reacts to context cancellation asynchronously. On SIGTERM, `<-ctx.Done()` fires in the `select`, `run()` returns immediately, and `defer shutdown.Shutdown()` begins closing publisher/DB while the Router is still draining in-flight message handlers.
2. **Consumer**: HealthServer goroutine starts before DI, but is only registered in shutdown after DI succeeds. DI failure leaks the goroutine.
3. **All entry points**: `defer` block accesses `app.ShutdownTimeout` — a nil dereference when DI fails and `app` is nil.

### Watermill Router Close Semantics

Key findings from Watermill v1.5.1 source analysis:

- `Router.Close()` is idempotent (guarded by `r.closed` bool + mutex)
- `Router.Run(ctx)` spawns a watcher that calls `Close()` on context cancellation
- `Run()` blocks until `Close()` completes (waits on `closedCh`)
- `Close()` calls `waitForHandlers()` which waits for all `runningHandlersWg` to drain
- Each handler closes its own subscriber and publisher on shutdown — but `AddNoPublisherHandler` (used by all consumer handlers via `AddConsumerHandler`) has no publisher to close
- The top-level publisher (registered in Flush phase) is **not** closed by Router

## Goals / Non-Goals

**Goals:**
- Ensure consumer shutdown phases execute only after all in-flight message handlers complete
- Prevent HealthServer goroutine leak on DI failure
- Prevent nil-pointer panic on DI failure across all entry points
- Maintain the existing phased shutdown contract (Drain → Flush → External → Observe → Datastore)

**Non-Goals:**
- Refactoring the shutdown package itself (global registry, `sync.Once` pattern)
- Adding shutdown integration tests (separate effort)
- Changing AckAsync behavior (existing ack semantics are correct for throughput)
- Modifying CronJob loop interruption patterns (already correct)

## Decisions

### D1: Wait for Router completion before shutdown phases

**Approach**: Restructure `cmd/consumer/main.go` so that `Router.Run(ctx)` completion is awaited **before** `shutdown.Shutdown()` runs.

Current flow (broken):
```
SIGTERM
  → ctx cancelled
  → select picks <-ctx.Done() immediately
  → return nil → defer shutdown.Shutdown() starts
  → Router still closing in background (race!)
```

New flow:
```
SIGTERM
  → ctx cancelled
  → select picks <-ctx.Done()
  → log shutdown signal
  → wait for Router.Run() to return via <-errChan  ← NEW
  → return nil → defer shutdown.Shutdown() starts
  → all handlers already drained, safe to close publisher/DB
```

Concretely, after `<-ctx.Done()` fires, we drain `errChan` to ensure `Router.Run()` has fully returned (and internally completed `Close()`). This mirrors the API server's pattern where `ConnectServer.Shutdown()` in Drain phase waits for in-flight requests.

**Why not register Router in Drain phase?** While `Router.Close()` is idempotent and the second call would block until the first completes, it creates a subtle dependency: shutdown correctness depends on the Watermill internal mutex behavior. Waiting for `Run()` to return is explicit, easier to reason about, and doesn't couple shutdown phases to library internals.

### D2: Defer HealthServer close unconditionally

**Approach**: Add `defer healthSrv.Close()` immediately after starting the goroutine, before DI initialization. This ensures cleanup on any exit path.

```go
healthSrv := server.NewHealthServer(":8081")
go func() { ... healthSrv.Start() ... }()
defer healthSrv.Close()  // ← always runs, even on DI failure

app, err := di.InitializeConsumerApp(ctx)
// ...
shutdown.AddDrainPhase(healthSrv)  // Drain phase calls Close() again — idempotent
```

`HealthServer.Close()` calls `http.Server.Shutdown()`, which is safe to call multiple times. The Drain phase registration still works because Shutdown is idempotent — the second call returns immediately.

### D3: Guard against nil app in defer across all entry points

**Approach**: Use a fallback timeout constant when `app` is nil.

```go
const fallbackShutdownTimeout = 10 * time.Second

defer func() {
    timeout := fallbackShutdownTimeout
    if app != nil {
        timeout = app.ShutdownTimeout
    }
    ctx, cancel := context.WithTimeout(context.Background(), timeout)
    defer cancel()
    if err := shutdown.Shutdown(ctx); err != nil {
        // Use bootLogger since app.Logger may also be nil
        bootLogger.Error(context.Background(), "error during shutdown", err)
    }
}()
```

This applies to all four entry points: `cmd/api/main.go`, `cmd/consumer/main.go`, `cmd/job/concert-discovery/main.go`, `cmd/job/artist-image-sync/main.go`.

**Why not skip shutdown entirely when app is nil?** Because partial DI initialization may have already opened resources (e.g., DB connection created before a later step fails). `shutdown.Shutdown()` with no registered closers is a no-op, so calling it is always safe.

## Risks / Trade-offs

**[Risk] Router.Run() hangs indefinitely** → Mitigated by Watermill's `CloseTimeout` config (defaults to 0 = no timeout). If a handler blocks forever, the consumer process would be SIGKILLed by K8s after `terminationGracePeriodSeconds`. Consider setting `RouterConfig.CloseTimeout` to align with the K8s budget in a follow-up.

**[Risk] Double-close of HealthServer** → `http.Server.Shutdown()` is documented as safe to call on an already-shut-down server. The defer close and Drain phase close are both safe.

**[Trade-off] Fallback timeout is a hardcoded constant** → Acceptable because the DI-failure path is an error recovery scenario where config is unavailable. 10s is generous for closing partially-initialized resources.
