## Why

The Go backend running on GKE Autopilot lacks robust graceful shutdown handling. During rolling deployments, the API server drops in-flight requests (502 errors) because there is no preStop hook to drain load balancer connections, and the health check continues reporting `Serving` after SIGTERM. The event consumer passes a cancelled context to its shutdown routine, risking silent resource cleanup failures. Resource teardown follows a flat ordering that can close the database before telemetry flushes its spans, and background goroutines are not tracked for completion.

## What Changes

- Implement phased shutdown orchestration with explicit ordering: signal → drain → flush → external clients → observability → datastore
- Add an `atomic.Bool` shutdown flag to the health check handler so it immediately returns `NotServing` upon SIGTERM, before `http.Server.Shutdown()` begins
- Track background goroutines with `sync.WaitGroup` / `errgroup` to guarantee completion before resource teardown
- Fix the consumer's cancelled-context bug (`cmd/consumer/main.go` passes already-cancelled ctx to `Shutdown`)
- Add explicit `Router.Close()` synchronization for Watermill consumer shutdown
- Add `preStop: exec: command: ["sleep", "5"]` and `terminationGracePeriodSeconds` to server, consumer, and cronjob K8s manifests
- Add readiness/liveness probes to the consumer deployment
- Upgrade `go.mod` to Go 1.26 and leverage `context.Cause()` for signal introspection logging

## Capabilities

### New Capabilities
- `graceful-shutdown`: Phased shutdown orchestration, health check state transitions, background goroutine lifecycle management, and timeout budget alignment between K8s and application

### Modified Capabilities
- `backend-service-exposure`: K8s deployment manifests gain `preStop` hooks, `terminationGracePeriodSeconds`, and consumer health probes

## Impact

- **Backend code** (`cmd/api`, `cmd/consumer`, `cmd/job`, `internal/di`, `internal/adapter/rpc`, `internal/infrastructure/server`, `pkg/config`): Shutdown flow restructured across all three entry points
- **K8s manifests** (`k8s/namespaces/backend/base/server/deployment.yaml`, `consumer/deployment.yaml`, `cronjob/cronjob.yaml`): New lifecycle hooks and probe configurations
- **Go module**: `go.mod` version bump from 1.25.7 to 1.26
- **No API breaking changes**: All changes are internal lifecycle management; no RPC contract changes
- **No database schema changes**
