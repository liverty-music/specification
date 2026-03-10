## Context

KEDA-scaled `consumer-app` pods in the dev cluster crash on startup with `dial tcp 10.30.13.1:4222: i/o timeout`. Three compounding issues were identified:

1. **KEDA consumer name mismatch** (root cause of unnecessary scale-out): The ScaledObject references `consumer: "consumer"`, but after PR #154 (stream naming refactor) the actual durable consumers are named `CONCERT_discovered` and `CONCERT_created`. KEDA cannot find `"consumer"`, interprets the entire stream message count (9,082) as lag, and permanently requests `maxReplicaCount: 3`.
2. **No initial connection retry**: `EnsureStreams()` calls `nats.Connect()` which fails immediately on TCP timeout. The `MaxReconnects(-1)` option only applies after an initial connection is established.
3. **Health server starts after DI**: Pods crash before K8s can observe them via probes, causing CrashLoopBackOff instead of a graceful "not ready" state.

Current consumer startup flow:
```
run()
  └─ InitializeConsumerApp(ctx)
      ├─ config, logger, DB pool         ← succeeds
      ├─ EnsureStreams(cfg.NATS)          ← nats.Connect() timeout → fatal
      ├─ NewPublisher(cfg.NATS, ...)      ← never reached
      └─ NewSubscriber(cfg.NATS, ...)     ← never reached
  └─ health server start                  ← never reached
  └─ router.Run(ctx)                      ← never reached
```

## Goals / Non-Goals

**Goals:**
- Eliminate unnecessary KEDA scale-out by fixing consumer name alignment
- Make consumer pods resilient to transient NATS unavailability during startup
- Allow K8s to distinguish "starting up" from "crashed" via health probes
- Make KEDA scaling parameters tunable per environment via Kustomize overlays

**Non-Goals:**
- Changing NATS stream topology or consumer semantics
- Modifying Watermill's internal connection handling
- Addressing GCE quota or node pool sizing (separate infrastructure concern)
- Adding health probe logic to the API server or job workloads

## Decisions

### Decision 1: Fix KEDA consumer name to `CONCERT_discovered`

**Choice**: Set ScaledObject `consumer` to `"CONCERT_discovered"`.

**Rationale**: KEDA's `nats-jetstream` scaler queries the NATS monitoring endpoint for a specific consumer's `num_pending`. The `CONCERT_discovered` consumer is the entry point of the pipeline (CronJob publishes → `CONCERT.discovered` → consumer processes). Its pending count accurately reflects unprocessed work. `CONCERT_created` is a downstream consumer and doesn't represent the primary ingestion backlog.

**Alternative considered**: Using `CONCERT_created` — rejected because it measures a different part of the pipeline and could mask ingestion lag.

### Decision 2: Retry loop in `EnsureStreams()` with context-aware backoff

**Choice**: Add a retry loop around `nats.Connect()` inside `EnsureStreams()`, with exponential backoff capped at 15 seconds, respecting the parent context for cancellation.

```
EnsureStreams(ctx, cfg) {
    backoff := [1s, 2s, 4s, 8s, 15s]
    for attempt := 0; ; attempt++ {
        nc, err := nats.Connect(url, Timeout(5s), ...)
        if err == nil → break
        select {
            case <-ctx.Done(): return err
            case <-time.After(backoff[min(attempt, len-1)]): continue
        }
    }
    // stream setup as before
}
```

**Rationale**: `RetryOnFailedConnect(true)` was considered but rejected — it returns a `RECONNECTING` client, and subsequent `JetStream()` API calls (StreamInfo, AddStream) fail on an unconnected client. A retry loop around the entire connect-then-setup sequence is simpler and guarantees streams are actually created before returning.

**Signature change**: `EnsureStreams(cfg)` → `EnsureStreams(ctx, cfg)` to enable context-aware cancellation. This propagates the signal context from `run()` so that SIGTERM during retry causes immediate exit.

**Also**: Increase `nats.Timeout` from default 2s to 5s per dial attempt. On freshly provisioned GKE Autopilot Spot nodes, kube-proxy rule propagation can take several seconds.

### Decision 3: Start health server before DI initialization

**Choice**: Start the health server in `run()` before calling `InitializeConsumerApp()`. The server initially reports `healthz=200` (alive) and `readyz=503` (not ready). After DI completes successfully, flip readiness to 200.

```
run() {
    healthSrv := server.NewHealthServer(":8081")
    go healthSrv.Start()                      // healthz=200, readyz=503

    app, err := InitializeConsumerApp(ctx)
    if err != nil { return err }

    healthSrv.SetReady()                      // readyz=200
    // ... router.Run(ctx)
}
```

**Rationale**: This separates "process is alive" from "process is ready to work". During NATS retry, the pod is alive but not ready. K8s won't kill it via liveness (which passes) and won't route traffic via readiness (which fails). This prevents CrashLoopBackOff escalation.

**Impact on HealthServer**: Requires adding a `SetReady()` method to toggle readiness state. Currently `HealthServer` is created inside DI — it needs to be created earlier in `run()` and passed into DI or removed from DI entirely.

### Decision 4: Parameterize KEDA values via Kustomize overlay patches

**Choice**: Keep base `scaledobject.yaml` with sensible defaults. Use Kustomize JSON patches in `overlays/dev/` to override `maxReplicaCount`, `lagThreshold`, and `activationLagThreshold`.

**Dev values**:
- `maxReplicaCount: 2` (reduce Spot node churn)
- `lagThreshold: "10"` (unchanged — appropriate for dev)
- `activationLagThreshold: "1"` (unchanged — scale from 0 on any pending message)

**Rationale**: Kustomize patches are the established pattern in this project for per-environment configuration. Environment variables are not applicable here — KEDA ScaledObject is a K8s resource, not a container config.

## Risks / Trade-offs

- **[Risk] Retry loop delays startup** → Mitigated by capping backoff at 15s and respecting context cancellation. Total worst-case startup delay before first NATS success: ~30s (1+2+4+8+15), well within liveness probe tolerance (10s initial + 3×20s = 70s).
- **[Risk] HealthServer refactor touches DI wiring** → Minimal: extract `NewHealthServer` from `InitializeConsumerApp` to `run()`, pass it in or remove it from DI. No business logic changes.
- **[Risk] KEDA consumer name becomes a coupling point** → If `DurableCalculator` logic changes, KEDA config must be updated in sync. Documented in tasks as a follow-up note.
- **[Trade-off] No `RetryOnFailedConnect` for Publisher/Subscriber** → After `EnsureStreams` succeeds, NATS TCP reachability is confirmed. Watermill creates connections immediately after. If a Publisher/Subscriber connection still fails, K8s restart handles it (now rare). Adding `RetryOnFailedConnect` to Watermill config is possible but adds complexity for minimal gain.
