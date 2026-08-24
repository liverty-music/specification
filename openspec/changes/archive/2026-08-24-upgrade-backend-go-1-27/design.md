## Context

See proposal.md — Why. Current state that shapes the approach:

- `backend/go.mod` is on `go 1.26` with the toolchain pinned to `1.26.6` for stdlib CVE fixes.
- All UUIDs come from `github.com/google/uuid v1.6.0`: 14 call sites across ~11 files, all `NewV7()` for IDs plus one `Parse()` in `internal/infrastructure/analytics/posthog/posthog_client.go`. A central helper `internal/entity` (`newID()` → `uuid.Must(uuid.NewV7()).String()`) exists but most repositories/usecases call `uuid.NewV7()` directly, so the abstraction is leaky.
- **No pprof/debug HTTP endpoint is currently mounted anywhere** in the backend.
- Monitoring is metric-based, with two distinct metric paths, both alerted on via Cloud Monitoring `AlertPolicy` (Pulumi, `cloud-provisioning`): (a) the backend's OTel SDK metrics flow OTLP → in-cluster otel-collector → `googlecloud` exporter, landing in **Cloud Monitoring** as `workload.googleapis.com/*` custom metrics; (b) Google Managed Prometheus (GMP, `PodMonitoring`) scrapes the prometheus-nats-exporter sidecar. Existing consumer health is alerted on `nats_consumer_num_pending` backlog (the GMP path) and liveness.
- Go 1.27 promotes the `goroutineleak` profile to GA (no `GOEXPERIMENT` needed) and makes the stdlib `uuid` package available; `go test` now runs the `stdversion` vet check by default.

## Goals / Non-Goals

**Goals:**
- Land the toolchain + `go` directive bump to 1.27 cleanly, including the one-time `go fix` modernizer diff.
- Detect silent goroutine wedges through an alertable metric, reusing the existing OTel-metric → Cloud Monitoring (`workload.googleapis.com`, via the otel-collector `googlecloud` exporter) → AlertPolicy path rather than inventing a new monitoring channel.
- Remove the `github.com/google/uuid` direct dependency with zero change to ID format or behavior.

**Non-Goals:**
- Migrating application code to the explicit `encoding/json/v2` API or tightening Gemini parse strictness (separate follow-on change; this change only inherits the implicit v2-backed speedup by upgrading).
- Adopting other 1.27 features (generic methods, `simd`, ML-DSA/post-quantum TLS — the backend imports no `crypto/tls`).
- Changing consumer backlog-stall or liveness alerting; leak detection is additive.

## Decisions

### D1: Two-step upgrade — toolchain first, then `go` directive, in one change
Bump the toolchain to 1.27.x and raise the `go 1.27` directive together, but treat them as ordered steps. Rationale: the stdlib `uuid` migration cannot compile until the directive is `1.27` (the package does not exist earlier and the new default `stdversion` vet check would flag it). Landing both in the same change keeps `go.mod` and the uuid migration consistent. Alternative (directive-only, keep old toolchain) rejected: the directive raises the language/stdlib floor, so the toolchain must match.

### D2: Route all UUID generation through the `entity` ID helper; parse stays local
Consolidate the 14 call sites to a single generation helper in `internal/entity` and update the lone `Parse` in `posthog_client.go` in place. Rationale: stdlib `uuid.NewV7()` returns `UUID` with **no error** (it panics internally on entropy failure) versus google/uuid's `(UUID, error)`. This deletes the `id, err := ...` / `if err != nil` boilerplate and the `uuid.Must` wrapper at every site, and the panic-on-entropy-failure semantics exactly match the existing helper's documented contract. Collapsing to one import site also makes the dependency swap a one-line edit and prevents the leaky abstraction from regrowing. Alternative (mechanical in-place swap at every site) rejected: same edit count, but leaves 11 direct imports and misses the consolidation win.

### D3: Alert on a leaked-goroutine **metric**, expose pprof for on-demand debugging
Two complementary surfaces:
- **Alerting path (primary):** a periodic in-process sampler looks up the `goroutineleak` profile, counts leaked goroutines, and publishes it as an OTel gauge (e.g. `backend_goroutine_leak_count`) with a workload label. A Cloud Monitoring `AlertPolicy` (Pulumi, alongside existing consumer alerts) fires when the value stays `> 0` beyond an evaluation window and auto-closes on recovery.
- **Debug path (secondary):** mount `net/http/pprof` (including the `goroutineleak` profile) on an **internal-only** listener (separate port, not the public Connect-RPC/ingress surface) so operators can pull a full profile with stacks on demand.

Rationale: their alerting is metric-driven, so a metric is the idiomatic escalation path and satisfies the spec's "alert without a user report"; the raw pprof endpoint satisfies the spec's "stack to identify the blocking site" for investigation. The gauge reaches **Cloud Monitoring** as a `workload.googleapis.com/backend_goroutine_leak_count` custom metric (OTLP → otel-collector `googlecloud` exporter — NOT Google Managed Prometheus, which only scrapes the nats exporter), so the AlertPolicy uses a **threshold** condition on it rather than a PromQL/GMP query. Alternative (log-based alert) rejected: log-based policies hit notificationRateLimit constraints and the team already standardizes on metric AlertPolicies. Alternative (public pprof) rejected on security grounds (spec forbids public unauthenticated exposure).

### D4: Sampling cadence is conservative and configurable
The `goroutineleak` profile analysis is not free (it inspects the runtime's goroutine set). Sample on a slow interval (order of minutes, env-configurable) rather than per-request or per-scrape. Rationale: leak detection is a slow-moving condition; a wedge that matters persists for minutes, so a coarse interval catches it while keeping overhead negligible. The evaluation window in the AlertPolicy — not the sampler — provides the transient-vs-sustained distinction the spec requires.

### D5: `make fix` runs `go fix ./...`; `make modernize` gate unchanged in shape
`make modernize` already fails closed on non-empty `go fix -diff ./...` — keep it. Fix the `make fix` gap so it runs `go fix ./...` (twice, for fixed point per Go guidance) in addition to `gofmt -w`, so the message "Run 'go fix ./...'" the gate prints is actually actionable via `make fix`. The 1.27 modernizer set changes (adds `atomictypes`/`embedlit`/`slicesbackward`/`unsafefuncs`, removes `fmtappendf`, renames `waitgroup`→`waitgroupgo`) are picked up automatically from the bundled toolchain; the one-time diff they produce is applied in this change.

## Risks / Trade-offs

- **`goroutineleak` profile blind spots** (leaks via global variables or via still-runnable goroutines are not reported) → Documented in the spec as a known limitation; leak alerting is additive to, not a replacement for, backlog-stall/liveness alerting, so those failure classes remain covered by existing signals.
- **NATS-internal wedges may not surface as Go-side blocked goroutines** (a durable misbind means "NATS isn't delivering," which may not block a Go goroutine on a primitive) → Same mitigation: backlog-stall alert stays as the complementary signal; leak alert catches the Go-side-blocked subset.
- **Sampling overhead / pause** from profile analysis → D4 coarse, configurable interval keeps cost negligible; can be disabled via config if it ever regresses.
- **`go fix` modernizer churn on the toolchain bump** (new modernizers rewrite existing code) → Apply and review the diff as ordinary code in this change from a clean tree, run twice to reach fixed point; CI gate then keeps it green going forward.
- **1.27 behavioral change: `time`-package channels are now always unbuffered/synchronous** (`asynctimerchan` GODEBUG removed) → Audit `time.After`/`Ticker` usage in `select` loops (consumers) during implementation; low likelihood given no reliance on buffered timer channels, but verify.
- **Removed GODEBUG settings fail the build if referenced** → `backend/go.mod` sets no GODEBUG values and the backend imports no `crypto/tls`; confirm no `//go:debug` directives before raising the directive.

## Migration Plan

1. Bump toolchain to 1.27.x in `backend/go.mod`; run `go build`/`go test` to confirm the runtime upgrade (malloc + json/v2-backed speedups land here with no code change).
2. Raise the `go 1.27` directive; run `go fix ./...` (×2) from a clean tree and commit the modernizer diff; fix `make fix`.
3. Migrate UUID call sites through the `entity` helper; drop `github.com/google/uuid`; `go mod tidy`.
4. Add the goroutine-leak sampler + OTel gauge and the internal pprof listener.
5. Provision the `AlertPolicy` in `cloud-provisioning`.
- **Rollback:** each step is independently revertible. The directive/toolchain bump and uuid swap revert as ordinary `go.mod`/code changes; the sampler and AlertPolicy can be removed without affecting request paths. No data migration is involved.
