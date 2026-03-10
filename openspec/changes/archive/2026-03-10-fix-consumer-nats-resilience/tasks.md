## 1. Fix KEDA consumer name and parameterize scaling

- [x] 1.1 Update `cloud-provisioning/k8s/namespaces/backend/base/consumer/scaledobject.yaml`: change `consumer: "consumer"` to `consumer: "CONCERT_discovered"`
- [x] 1.2 Create `cloud-provisioning/k8s/namespaces/backend/overlays/dev/` patch for `maxReplicaCount: 2`
- [x] 1.3 Verify rendered manifest with `kubectl kustomize` for dev overlay

## 2. Add NATS connection retry to EnsureStreams

- [x] 2.1 Change `EnsureStreams` signature from `EnsureStreams(cfg config.NATSConfig)` to `EnsureStreams(ctx context.Context, cfg config.NATSConfig)` in `backend/internal/infrastructure/messaging/streams.go`
- [x] 2.2 Add retry loop with exponential backoff (1s, 2s, 4s, 8s, 15s cap) around `nats.Connect()`, respecting `ctx.Done()` for cancellation
- [x] 2.3 Add `nats.Timeout(5 * time.Second)` to connection options
- [x] 2.4 Update all callers of `EnsureStreams`: `internal/di/consumer.go`, `internal/di/app.go`, `internal/di/job.go`

## 3. Start health server before DI

- [x] 3.1 Add `SetReady()` method to `HealthServer` that toggles readiness from 503 to 200
- [x] 3.2 Move `HealthServer` creation from `InitializeConsumerApp` to `run()` in `cmd/consumer/main.go`
- [x] 3.3 Start health server before `InitializeConsumerApp()`, call `SetReady()` after DI succeeds
- [x] 3.4 Remove `HealthServer` from `ConsumerApp` struct and `InitializeConsumerApp` return value

## 4. Verify

- [x] 4.1 Run `make check` in backend repo (lint + test)
- [x] 4.2 Run `make check` in cloud-provisioning repo (lint-ts + lint-k8s)
