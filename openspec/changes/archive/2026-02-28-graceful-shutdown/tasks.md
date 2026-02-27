## 1. Go Module Upgrade

- [x] 1.1 Upgrade `go.mod` from `go 1.25.7` to `go 1.26` and run `go mod tidy`

## 2. Shutdown Manager

- [x] 2.1 Create `internal/di/shutdown.go` with `ShutdownManager` type supporting named phases and `sync.WaitGroup` integration
- [x] 2.2 Write unit tests for `ShutdownManager` — verify phase ordering, error aggregation, context deadline enforcement

## 3. Health Check Shutdown State

- [x] 3.1 Add `shuttingDown atomic.Bool` to `HealthCheckHandler` with `SetShuttingDown()` method; return `StatusNotServing` when flag is set
- [x] 3.2 Write unit test verifying health check returns `StatusNotServing` after `SetShuttingDown()` is called

## 4. API Server Shutdown Refactor

- [x] 4.1 Refactor `internal/di/app.go` — replace flat `[]io.Closer` with `ShutdownManager` phased shutdown (drain → flush → external → observe → datastore)
- [x] 4.2 Refactor `internal/di/provider.go` — register closers into named phases; pass `HealthCheckHandler` to `App` so `SetShuttingDown()` can be called at shutdown start
- [x] 4.3 Track cache cleanup goroutine with `sync.WaitGroup` in `provider.go` and add `wg.Wait()` in the drain phase
- [x] 4.4 Update `cmd/api/main.go` — use `context.Cause(ctx)` for signal introspection logging (Go 1.26 feature)

## 5. Consumer Shutdown Refactor

- [x] 5.1 Fix cancelled-context bug in `cmd/consumer/main.go` — pass `context.Background()` to `app.Shutdown()`
- [x] 5.2 Restructure consumer main to run `Router.Run(ctx)` in goroutine, then call `Router.Close()` explicitly after ctx cancellation
- [x] 5.3 Refactor `internal/di/consumer.go` — use `ShutdownManager` with phased shutdown
- [x] 5.4 Add lightweight HTTP health server to consumer (`/healthz`, `/readyz` on port 8081) with shutdown flag integration

## 6. Job Shutdown Refactor

- [x] 6.1 Refactor `internal/di/job.go` — use `ShutdownManager` with phased shutdown

## 7. K8s Manifest Updates

- [x] 7.1 Add `terminationGracePeriodSeconds: 60` and `preStop: exec: command: ["sleep", "5"]` to server `deployment.yaml`
- [x] 7.2 Add `terminationGracePeriodSeconds: 90`, `preStop: exec: command: ["sleep", "5"]`, readiness probe (HTTP `/readyz` port 8081), and liveness probe (HTTP `/healthz` port 8081) to consumer `deployment.yaml`
- [x] 7.3 Add `terminationGracePeriodSeconds: 120` to cronjob `cronjob.yaml`
- [x] 7.4 Update `SHUTDOWN_TIMEOUT` in server configmap to `45s` and consumer configmap to `60s`
- [x] 7.5 Run `kubectl kustomize` dry-run on all dev overlays to verify rendered manifests

## 8. Verification

- [x] 8.1 Run full test suite (`go test ./...`) and linters (`golangci-lint run`)
- [x] 8.2 Verify Go 1.26 build succeeds with no regressions
