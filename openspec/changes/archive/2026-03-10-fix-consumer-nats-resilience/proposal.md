## Why

KEDA-scaled `consumer-app` pods crash on startup with NATS connection timeout (`dial tcp 10.30.13.1:4222: i/o timeout`), leaving the ArgoCD `backend` application in Degraded state since 2026-02-21. Investigation revealed three compounding issues: (1) the KEDA ScaledObject references a non-existent consumer name `"consumer"`, causing unnecessary scale-out even when all messages are fully consumed, (2) `EnsureStreams()` has no retry on initial NATS connection, and (3) health probes don't start until after DI completes, so pods crash before K8s can observe them.

## What Changes

- **Fix KEDA consumer name mismatch**: Update `scaledobject.yaml` consumer from `"consumer"` to `"CONCERT_discovered"` to match the actual durable consumer name created by Watermill's `DurableCalculator`
- **Parameterize KEDA ScaledObject values**: Extract `lagThreshold`, `activationLagThreshold`, and `maxReplicaCount` into Kustomize overlay patches so they can be tuned per environment
- **Set dev `maxReplicaCount` to 2**: Reduce unnecessary Spot node provisioning in dev
- **Add NATS connection retry with backoff**: Wrap `EnsureStreams()` initial connection in a retry loop with exponential backoff, respecting context cancellation
- **Start health server before DI**: Move health server startup before `InitializeConsumerApp()` so K8s can distinguish "starting up" from "crashed"

## Capabilities

### New Capabilities

_None — this is an infrastructure reliability fix with no new user-facing capabilities._

### Modified Capabilities

_None — no spec-level behavior changes. All changes are internal to deployment and startup resilience._

## Impact

- **cloud-provisioning**: `k8s/namespaces/backend/base/consumer/scaledobject.yaml`, dev overlay patch for KEDA values
- **backend**: `internal/infrastructure/messaging/streams.go` (retry logic), `cmd/consumer/main.go` (health server startup order), `internal/di/consumer.go` (signature change for `EnsureStreams`)
- **NATS JetStream**: No stream or consumer schema changes — fix aligns KEDA config with existing consumer names
- **ArgoCD**: Degraded state will resolve once KEDA stops triggering unnecessary scale-out
