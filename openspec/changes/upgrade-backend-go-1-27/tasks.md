## 1. Toolchain upgrade (runtime speedups, no code change)

- [ ] 1.1 Confirm no `//go:debug` directives or removed GODEBUG settings in `backend/go.mod` / sources (e.g. `asynctimerchan`); backend imports no `crypto/tls`, so TLS GODEBUG removals are N/A
- [ ] 1.2 Bump the toolchain to Go 1.27.x in `backend/go.mod`
- [ ] 1.3 Run `go build ./...` and `go test ./...`; verify green (inherits size-specialized malloc + `json/v2`-backed `encoding/json` speedups for free)
- [ ] 1.4 Audit `time.After` / `time.Ticker` usage in consumer `select` loops for reliance on the old buffered timer-channel behavior (now always unbuffered)

## 2. Raise `go` directive and apply modernizers

- [ ] 2.1 Raise the `go 1.27` directive in `backend/go.mod`
- [ ] 2.2 From a clean tree, run `go fix ./...` twice (fixed point) and commit the modernizer diff for the 1.27 set (`atomictypes`/`embedlit`/`slicesbackward`/`unsafefuncs`; `waitgroup`→`waitgroupgo`; `fmtappendf` removed)
- [ ] 2.3 Update `make fix` to run `go fix ./...` (×2) in addition to `gofmt -w .`
- [ ] 2.4 Run `make modernize` and `go test ./...` (now including the default `stdversion` vet check) and confirm both pass

## 3. Migrate to stdlib `uuid`, drop google/uuid

- [ ] 3.1 Update `internal/entity` ID helper to use stdlib `uuid.NewV7().String()` (drop the `uuid.Must` / error handling)
- [ ] 3.2 Route the 14 `uuid.NewV7()` generation call sites (in `internal/usecase/*`, `internal/infrastructure/database/rdb/*`, `internal/infrastructure/messaging/cloudevents.go`) through the `entity` helper; delete their local `id, err := ...` boilerplate
- [ ] 3.3 Switch the `Parse` call in `internal/infrastructure/analytics/posthog/posthog_client.go` to stdlib `uuid.Parse`
- [ ] 3.4 Remove `github.com/google/uuid` from imports and run `go mod tidy`; confirm it is gone from direct requires
- [ ] 3.5 Run tests and verify generated IDs remain UUIDv7 with identical string format (existing ID/entity tests pass)

## 4. Goroutine leak detection — metric + pprof (spec: goroutine-leak-detection)

- [ ] 4.1 Add an internal-only HTTP listener that mounts `net/http/pprof` including the `goroutineleak` profile, on a separate non-public port (not the Connect-RPC/ingress surface)
- [ ] 4.2 Add a periodic sampler that looks up the `goroutineleak` profile, counts leaked goroutines, and publishes an OTel gauge (e.g. `backend_goroutine_leak_count`) with a workload label; interval is env-configurable and coarse (minutes)
- [ ] 4.3 Verify the profile is empty on a healthy instance and that a deliberately wedged goroutine (test/staging) appears with its stack and increments the gauge
- [ ] 4.4 Confirm the pprof listener is not reachable on any public/unauthenticated route

## 5. Alerting and documentation

- [ ] 5.1 Provision a Cloud Monitoring `AlertPolicy` (Pulumi, `cloud-provisioning`, alongside existing consumer alerts) that fires when `backend_goroutine_leak_count > 0` beyond the evaluation window and auto-closes on recovery, notifying the ops channel and identifying the workload
- [ ] 5.2 Validate the metric ingests in GMP and the alert previews without apply-time errors (disableMetricValidation if not-yet-ingested)
- [ ] 5.3 Document the capability's known blind spots (leaks via globals / still-runnable goroutines) and its complementary relationship to backlog-stall & liveness alerting
- [ ] 5.4 Run the full `make check` (lint + schema-lint + modernize + test) and confirm green
