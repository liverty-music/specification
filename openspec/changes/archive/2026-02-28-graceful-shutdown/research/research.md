# Research: Graceful Shutdown for K8s Go Backend

**Date**: 2026-02-27
**Scope**: API Server, Event Consumer, CronJob
**Go Version**: go 1.25.7 (go.mod) — upgrade target: Go 1.26

---

## 1. Current Implementation Audit

### 1.1 Architecture Overview

```
                    K8s Pod Termination
                           │
                      SIGTERM (PID 1)
                           │
                    signal.NotifyContext()
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         cmd/api      cmd/consumer   cmd/job
              │            │            │
         App.Shutdown  ConsumerApp   JobApp
              │         .Shutdown    .Shutdown
              │            │            │
         ┌────┴────┐   ┌──┴──┐     ┌──┴──┐
         │Server   │   │for  │     │for  │
         │.Stop()  │   │range│     │range│
         │         │   │close│     │close│
         │for range│   │rs   │     │rs   │
         │closers  │   └─────┘     └─────┘
         └─────────┘
```

### 1.2 Component-by-Component Analysis

#### API Server (`cmd/api/main.go`)

| Aspect | Current State | Assessment |
|--------|--------------|------------|
| Signal handling | `signal.NotifyContext(SIGINT, SIGTERM, SIGQUIT)` | OK — standard pattern |
| Server shutdown | `http.Server.Shutdown(ctx)` with 30s timeout | OK — drains in-flight HTTP requests |
| Closer ordering | Server → DB → Telemetry → LastFM → MusicBrainz → Publisher → [SBT] | **ISSUE**: DB closed before telemetry flushes spans that may reference DB |
| Background goroutine | Cache cleanup ticker, uses `ctx.Done()` | **ISSUE**: No `sync.WaitGroup` — goroutine leaks possible |
| Health check during shutdown | Returns `StatusServing` until DB is closed | **CRITICAL**: Should return `StatusNotServing` immediately on SIGTERM |

#### Event Consumer (`cmd/consumer/main.go`)

| Aspect | Current State | Assessment |
|--------|--------------|------------|
| Signal handling | `signal.NotifyContext(SIGINT, SIGTERM, SIGQUIT)` | OK |
| Router shutdown | `Router.Run(ctx)` blocks, cancelled by ctx | **ISSUE**: No explicit `Router.Close()` — relies solely on ctx cancellation |
| Shutdown passes **cancelled ctx** | `app.Shutdown(ctx)` where ctx is already Done | **CRITICAL BUG**: All closers receive a cancelled context. Telemetry flush and DB close may fail |
| Health probes | **NONE** | **CRITICAL**: K8s cannot detect consumer hangs |

#### CronJob (`cmd/job/concert-discovery/main.go`)

| Aspect | Current State | Assessment |
|--------|--------------|------------|
| Signal handling | Same pattern | OK |
| terminationGracePeriodSeconds | Not set (default 30s) | Should match job duration or have explicit timeout |
| Resource cleanup | `closers: []io.Closer{db, telemetryCloser, publisher}` | OK for batch job |

### 1.3 Kubernetes Manifest Gaps

```
SERVER DEPLOYMENT                    CONSUMER DEPLOYMENT
─────────────────                    ───────────────────
terminationGracePeriodSeconds: ❌     terminationGracePeriodSeconds: ❌
  (defaults to 30s)                    (defaults to 30s)

preStop hook: ❌                      preStop hook: ❌
  (needed for LB draining)             (needed for NATS draining)

readinessProbe: ✅ (gRPC)            readinessProbe: ❌
livenessProbe: ✅ (gRPC)             livenessProbe: ❌

strategy:                            strategy:
  maxUnavailable: 0 ✅                 (not configured)
```

---

## 2. Identified Issues (Priority Order)

### 2.1 CRITICAL — Consumer Shutdown Uses Cancelled Context

**File**: `cmd/consumer/main.go:41`

```go
defer func() {
    if err := app.Shutdown(ctx); err != nil {  // ctx is ALREADY cancelled here!
        app.Logger.Error(ctx, "error during shutdown", err)
    }
}()
```

When `Router.Run(ctx)` returns (because ctx was cancelled by SIGTERM), the deferred `app.Shutdown(ctx)` passes a **cancelled context** to all closers. This means:
- `telemetry.tracerCloser.Close()` creates a new context internally — **OK but wasteful**
- `pgxpool.Pool.Close()` does not use context — **OK**
- Any future closer that requires a live context will **fail silently**

**Fix**: Pass `context.Background()` like the API server does.

### 2.2 CRITICAL — No Readiness State Transition on Shutdown

**File**: `internal/adapter/rpc/health_handler.go`

The health check only pings the DB. When SIGTERM is received:
1. K8s sends SIGTERM
2. K8s **concurrently** removes Pod from Service endpoints
3. But endpoint removal is **eventually consistent** (kube-proxy/iptables update lag)
4. During this window, new requests still arrive at the Pod
5. Health check still returns `StatusServing`
6. `http.Server.Shutdown()` starts, refusing new connections

**The gap**: Between SIGTERM and `http.Server.Shutdown()` completing its listener close, requests that arrive find a "serving" health check but may get connection refused.

**Fix**: Health check should immediately return `StatusNotServing` when shutdown begins, before `http.Server.Shutdown()` is called.

### 2.3 CRITICAL — No preStop Hook for Load Balancer Draining

K8s termination sequence:

```
  ┌──────────────────────────────────────────────────────┐
  │                K8s Termination                       │
  │                                                      │
  │  SIGTERM ──────────────────────┐                     │
  │       │                        │                     │
  │       ▼                        ▼                     │
  │  ┌──────────┐          ┌──────────────┐              │
  │  │ preStop  │          │ Endpoint     │              │
  │  │  hook    │          │ removal      │              │
  │  │ (none!)  │          │ (async,      │              │
  │  └────┬─────┘          │  5-10s lag)  │              │
  │       │                └──────────────┘              │
  │       ▼                                              │
  │  SIGTERM delivered                                   │
  │  to PID 1                                            │
  │       │                                              │
  │       ▼                                              │
  │  App shutdown starts                                 │
  │  (server accepts NO new connections)                 │
  │       │                                              │
  │       ▼                                              │
  │  ⚠ RACE: LB still sends traffic                     │
  │    but server already closed listener                │
  │    → 502 / connection refused                        │
  └──────────────────────────────────────────────────────┘
```

**Fix**: Add `preStop: exec: command: ["sleep", "5"]` to give the endpoints controller time to update. The 5s delay ensures in-flight routing converges before the app begins shutdown.

### 2.4 HIGH — Shutdown Ordering is Flat, Not Phased

Current order (`provider.go:260`):
```go
closers := []io.Closer{db, telemetryCloser, lastfmClient, musicbrainzClient, publisher}
```

This is a single flat slice — all closed in order with no phasing. If DB closes before telemetry, any in-flight span referencing DB activity loses its context.

**Ideal shutdown ordering** (reverse dependency order):

```
Phase 1: Stop accepting work
  ├─ Health → NotServing (signal external systems)
  └─ HTTP Server.Shutdown() (drain in-flight requests)

Phase 2: Drain async producers
  └─ Publisher.Close() (flush pending NATS messages)

Phase 3: Close external API clients
  ├─ LastFM client
  ├─ MusicBrainz client
  └─ Blockchain SBT client

Phase 4: Flush observability
  └─ Telemetry (flush pending OTel spans)

Phase 5: Close data stores (last)
  └─ Database pool + Cloud SQL dialer
```

### 2.5 HIGH — Background Goroutine Not Tracked

**File**: `internal/di/provider.go:102-113`

```go
go func() {
    ticker := time.NewTicker(10 * time.Minute)
    defer ticker.Stop()
    for {
        select {
        case <-ctx.Done():
            return
        case <-ticker.C:
            artistCache.Cleanup()
        }
    }
}()
```

This goroutine is fire-and-forget. No `sync.WaitGroup` tracks its completion. If shutdown is triggered between `case <-ticker.C` and `Cleanup()` completing, the goroutine may still be running when DB is closed.

**Fix**: Use `errgroup.Group` or `sync.WaitGroup` to track all background goroutines and wait for them during shutdown.

### 2.6 HIGH — Consumer Has No Health Probes

**File**: `k8s/namespaces/backend/base/consumer/deployment.yaml`

The consumer deployment has zero health probes. This means:
- K8s cannot detect if the consumer is hung
- K8s cannot detect if NATS connection is lost
- No readiness gate for rolling updates
- Pod restarts rely only on process exit

### 2.7 MEDIUM — Timeout Budget Not Aligned

```
K8s terminationGracePeriodSeconds: 30s (default)
App SHUTDOWN_TIMEOUT:              30s (default)
preStop hook:                       0s (none exists)

Budget: preStop + appShutdown + buffer ≤ terminationGracePeriod
Current: 0 + 30 + 0 = 30  (no buffer, tight race)
```

If we add a 5s preStop, the app only has 25s to shutdown before SIGKILL. But the app's internal timeout is still 30s → the app may be killed mid-shutdown.

**Fix**:
- `terminationGracePeriodSeconds: 60`
- `preStop: sleep 5`
- `SHUTDOWN_TIMEOUT: 45s`
- Budget: 5 + 45 + 10(buffer) = 60

### 2.8 MEDIUM — Watermill Router Shutdown Not Synchronized

The consumer relies on `Router.Run(ctx)` returning when ctx is cancelled. But Watermill's `Router.Close()` method provides a controlled shutdown that:
1. Stops accepting new messages
2. Waits for in-flight handlers to complete (up to `CloseTimeout`)
3. Closes publishers and subscribers

Currently, ctx cancellation triggers Router shutdown, but the deferred `app.Shutdown()` also closes the publisher independently — potential double-close or race.

### 2.9 LOW — No Structured Shutdown Logging

Shutdown events are logged as individual messages without correlation. For observability, shutdown should emit structured events with:
- Phase transitions
- Duration of each phase
- Which closers succeeded/failed
- Total shutdown duration

---

## 3. Go 1.26 Features Relevant to Graceful Shutdown

### 3.1 `signal.NotifyContext` with `CancelCauseFunc` (NEW in 1.26)

Go 1.26 enhances `signal.NotifyContext` to cancel the returned context with a cause error indicating which signal was received.

```go
ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGTERM, os.Interrupt)
defer stop()

<-ctx.Done()
cause := context.Cause(ctx)
// cause contains the signal information — e.g., "signal: terminated"
```

**Benefit**: Better shutdown observability — log which exact signal triggered shutdown.

### 3.2 Experimental Goroutine Leak Detection (NEW in 1.26)

Build with `GOEXPERIMENT=goroutineleakprofile` to enable:
- New `/debug/pprof/goroutineleak` endpoint
- Detects goroutines blocked on unreachable concurrency primitives
- Uses GC reachability analysis

**Benefit**: Detect goroutine leaks during shutdown (e.g., the cache cleanup goroutine if it gets stuck).

### 3.3 Green Tea GC (Default in 1.26)

- 10-40% reduction in GC overhead
- Better small object locality

**Benefit**: Faster cleanup during shutdown phase when many objects are being finalized.

### 3.4 `http.HTTP2Config.StrictMaxConcurrentRequests` (NEW in 1.26)

Controls stream limit behavior for HTTP/2. Useful for Connect-RPC which uses HTTP/2 over h2c.

**Benefit**: Better connection management during graceful shutdown — prevents new streams from being opened on connections being drained.

---

## 4. Best Practices for K8s Graceful Shutdown (2026)

### 4.1 Pod Termination Lifecycle (Complete)

```
1. Pod marked for deletion
2. Pod state → Terminating
3. CONCURRENT:
   a. preStop hook runs (if defined)
   b. Pod removed from Service endpoints (async, 2-10s lag)
4. After preStop completes → SIGTERM sent to PID 1
5. App handles SIGTERM:
   a. Stop accepting new work
   b. Drain in-flight requests
   c. Close resources in reverse dependency order
   d. Flush observability data
6. Process exits
7. If not exited within terminationGracePeriodSeconds → SIGKILL
```

### 4.2 Recommended Timeout Budget Formula

```
terminationGracePeriodSeconds = preStopDelay + appShutdownTimeout + safetyBuffer

Example for API Server:
  60s = 5s (preStop) + 45s (app shutdown) + 10s (safety buffer)

Example for Consumer:
  90s = 5s (preStop) + 60s (message handler drain) + 25s (safety buffer)
```

### 4.3 Health Check State Machine

```
          ┌──────────┐
          │ Starting │ ── startupProbe passes ──▶ ┌─────────┐
          └──────────┘                            │ Serving │
                                                  └────┬────┘
                                                       │
                                                  SIGTERM received
                                                       │
                                                       ▼
                                                ┌──────────────┐
                                                │ Not Serving  │
                                                │  (draining)  │
                                                └──────┬───────┘
                                                       │
                                                  all requests drained
                                                       │
                                                       ▼
                                                ┌──────────────┐
                                                │   Stopped    │
                                                └──────────────┘
```

The health handler MUST atomically transition to `NotServing` when SIGTERM is received, BEFORE `http.Server.Shutdown()` begins. This ensures:
1. K8s readiness probe fails → endpoint removed faster
2. GCP load balancer health check fails → traffic shifted
3. In-flight requests complete normally via `Shutdown()` drain

### 4.4 Connect-RPC Specific Considerations

Connect-RPC runs on `net/http` — it does NOT have gRPC's `GracefulStop()` or connection draining. Key differences:

| gRPC-Go | Connect-RPC (net/http) |
|---------|----------------------|
| `grpcServer.GracefulStop()` | `httpServer.Shutdown(ctx)` |
| Sends GOAWAY to clients | Closes listener, drains connections |
| Stream-aware draining | HTTP/2 connection-level draining |
| Built-in drain support | No explicit stream draining |

**For Connect-RPC streaming endpoints**: `http.Server.Shutdown()` will wait for handlers to return. Streaming handlers MUST respect context cancellation to avoid blocking shutdown indefinitely.

### 4.5 Watermill Router Shutdown Best Practice

```go
// Current (implicit):
router.Run(ctx)  // blocks until ctx cancelled
// Router internally calls Close() when ctx is done

// Recommended (explicit):
go router.Run(ctx)

<-ctx.Done()
if err := router.Close(); err != nil {
    logger.Error("router close failed", err)
}
// Then close other resources
```

With explicit `Router.Close()`, you get:
- Controlled `CloseTimeout` enforcement
- Error reporting on incomplete handlers
- Guaranteed publisher/subscriber cleanup before manual closer iteration

---

## 5. Proposed Shutdown Architecture

### 5.1 Target Design

```
                         SIGTERM
                           │
                    signal.NotifyContext()
                    (Go 1.26: cause-aware)
                           │
                    context.Cause(ctx) → log signal
                           │
                           ▼
               ┌───────────────────────┐
               │  Phase 0: Signal      │
               │  • Set shutdown flag  │
               │  • Health → NotServing│
               │  • preStop already    │
               │    gave LB 5s head    │
               │    start              │
               └───────────┬───────────┘
                           │
               ┌───────────▼───────────┐
               │  Phase 1: Drain       │
               │  • Server.Shutdown()  │
               │    (wait in-flight)   │
               │  • WaitGroup for bg   │
               │    goroutines         │
               └───────────┬───────────┘
                           │
               ┌───────────▼───────────┐
               │  Phase 2: Flush       │
               │  • Publisher.Close()  │
               │  • Flush NATS buffers │
               └───────────┬───────────┘
                           │
               ┌───────────▼───────────┐
               │  Phase 3: External    │
               │  • Close API clients  │
               │  • LastFM, MusicBrainz│
               │  • Blockchain         │
               └───────────┬───────────┘
                           │
               ┌───────────▼───────────┐
               │  Phase 4: Observe     │
               │  • Telemetry flush    │
               │  • Final spans/logs   │
               └───────────┬───────────┘
                           │
               ┌───────────▼───────────┐
               │  Phase 5: Data Store  │
               │  • pgxpool.Close()    │
               │  • CloudSQL dialer    │
               └───────────┬───────────┘
                           │
                       Process Exit
```

### 5.2 K8s Manifest Changes

```yaml
# Server Deployment
spec:
  template:
    spec:
      terminationGracePeriodSeconds: 60
      containers:
      - name: server
        lifecycle:
          preStop:
            exec:
              command: ["sleep", "5"]

# Consumer Deployment
spec:
  template:
    spec:
      terminationGracePeriodSeconds: 90
      containers:
      - name: consumer
        lifecycle:
          preStop:
            exec:
              command: ["sleep", "5"]
        # ADD readiness and liveness probes (HTTP or exec-based)

# CronJob
spec:
  jobTemplate:
    spec:
      template:
        spec:
          terminationGracePeriodSeconds: 120
```

### 5.3 Shutdown Manager Pattern

Instead of a flat `[]io.Closer`, introduce a `ShutdownManager` that:
1. Registers resources with shutdown phases/priorities
2. Executes phases in order with per-phase timeouts
3. Logs phase transitions with structured fields
4. Returns aggregated errors
5. Respects a global deadline from `terminationGracePeriodSeconds`

```
ShutdownManager
  ├── Phase(0, "signal")     → set shutdown flag, health → not serving
  ├── Phase(1, "drain")      → server.Shutdown(), waitgroup.Wait()
  ├── Phase(2, "flush")      → publisher, NATS
  ├── Phase(3, "external")   → API clients
  ├── Phase(4, "observe")    → telemetry
  └── Phase(5, "datastore")  → database
```

### 5.4 Health Check Enhancement

```go
type HealthCheckHandler struct {
    db          *rdb.Database
    logger      *logging.Logger
    shuttingDown atomic.Bool   // NEW: shutdown state flag
}

func (h *HealthCheckHandler) SetShuttingDown() {
    h.shuttingDown.Store(true)
}

func (h *HealthCheckHandler) Check(ctx context.Context, req *grpchealth.CheckRequest) (*grpchealth.CheckResponse, error) {
    if h.shuttingDown.Load() {
        return &grpchealth.CheckResponse{Status: grpchealth.StatusNotServing}, nil
    }
    // ... existing DB ping logic
}
```

---

## 6. Summary of Changes Required

### Backend Code (github.com/liverty-music/backend)

| # | Priority | Component | Change |
|---|----------|-----------|--------|
| 1 | CRITICAL | `cmd/consumer/main.go` | Pass `context.Background()` to `app.Shutdown()` |
| 2 | CRITICAL | `internal/adapter/rpc/health_handler.go` | Add `atomic.Bool` shutdown flag, return `NotServing` on SIGTERM |
| 3 | HIGH | `internal/di/app.go` | Implement phased shutdown (signal → drain → flush → external → observe → datastore) |
| 4 | HIGH | `internal/di/provider.go` | Track background goroutines with `errgroup` or `sync.WaitGroup` |
| 5 | HIGH | `internal/di/consumer.go` | Explicit `Router.Close()` call with timeout instead of relying on ctx |
| 6 | MEDIUM | `cmd/api/main.go` | Use Go 1.26 `context.Cause(ctx)` for signal introspection logging |
| 7 | MEDIUM | `pkg/config/config.go` | Separate per-phase timeouts or keep single timeout with phase budget |
| 8 | LOW | All apps | Add structured shutdown logging (phase, duration, errors) |

### K8s Manifests (github.com/liverty-music/cloud-provisioning)

| # | Priority | Manifest | Change |
|---|----------|----------|--------|
| 1 | CRITICAL | `server/deployment.yaml` | Add `preStop: sleep 5`, `terminationGracePeriodSeconds: 60` |
| 2 | CRITICAL | `consumer/deployment.yaml` | Add health probes, `preStop: sleep 5`, `terminationGracePeriodSeconds: 90` |
| 3 | MEDIUM | `cronjob.yaml` | Add `terminationGracePeriodSeconds: 120` |

### Go Module

| # | Priority | Change |
|---|----------|--------|
| 1 | MEDIUM | Upgrade `go.mod` from go 1.25.7 to go 1.26 for `signal.NotifyContext` cause-aware cancellation |

---

## 7. References

- [Go 1.26 Release Notes](https://go.dev/doc/go1.26) — signal.NotifyContext CancelCauseFunc, goroutine leak detection
- [Go 1.26 Blog Post](https://go.dev/blog/go1.26) — Green Tea GC, HTTP/2 config
- [Kubernetes: Terminating with Grace](https://cloud.google.com/blog/products/containers-kubernetes/kubernetes-best-practices-terminating-with-grace) — Google best practices
- [CNCF: Pod Termination Lifecycle](https://www.cncf.io/blog/2024/12/19/decoding-the-pod-termination-lifecycle-in-kubernetes-a-comprehensive-guide/) — Complete lifecycle guide
- [Go Graceful Shutdown for Kubernetes (2026)](https://oneuptime.com/blog/post/2026-01-07-go-graceful-shutdown-kubernetes/view) — Timeout budget formula
- [Graceful Shutdown Handlers for Long-Running K8s Processes](https://oneuptime.com/blog/post/2026-02-09-graceful-shutdown-handlers/view) — Handler draining patterns
- [gRPC Graceful Shutdown Guide](https://grpc.io/docs/guides/server-graceful-stop/) — GracefulStop vs Connect-RPC differences
- [Watermill Router Documentation](https://watermill.io/docs/messages-router/) — Router.Close(), CloseTimeout
- [Watermill Issue #446](https://github.com/ThreeDotsLabs/watermill/issues/446) — Router closes publisher before handler completion
- [Connect-RPC FAQ](https://connectrpc.com/docs/faq/) — Streaming shutdown considerations
- [VictoriaMetrics: Go Graceful Shutdown Patterns](https://victoriametrics.com/blog/go-graceful-shutdown/) — Practical patterns
- [net/http HTTP/2 Shutdown Issue #39776](https://github.com/golang/go/issues/39776) — HTTP/2 connection draining caveats
