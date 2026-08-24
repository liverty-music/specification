## Why

Go 1.27 (August 2026) ships changes that map directly onto this backend's operational pain and dependency surface: a GA `goroutineleak` runtime profile that detects goroutines permanently blocked on channels/mutexes — the exact failure class behind our repeated JetStream consumer wedge outages that fired no alert — plus a size-specialized allocator and a `json/v2`-backed `encoding/json` that speed up our allocation- and JSON-heavy RPC/event paths for free. The release also adds a standard-library `uuid` package that covers everything we use, letting us drop the `github.com/google/uuid` direct dependency. Upgrading now, while the toolchain pin is already carrying stdlib CVE fixes, keeps us on a supported, hardened runtime.

## What Changes

- Upgrade the backend Go toolchain from 1.26 to 1.27, then raise the `go` directive in `backend/go.mod` to `1.27` (unlocks the stdlib `uuid` package and enables the `stdversion` vet check `go test` now runs by default).
- **Enable goroutine leak detection**: expose the GA `runtime/pprof` `goroutineleak` profile (via `/debug/pprof/goroutineleak`) and wire it into monitoring/alerting so silent consumer wedges surface as an alert rather than a user-reported outage.
- Migrate all UUID generation/parsing from `github.com/google/uuid` to the standard-library `uuid` package (V7 for IDs, `Parse` for validation), consolidating call sites through the existing `entity` ID helper, and **remove the `github.com/google/uuid` direct dependency**.
- Adopt the size-specialized allocator and the `json/v2`-backed `encoding/json` implicitly by upgrading (no code change); optionally tighten Gemini LLM-output parsing against `json/v2` strict semantics (reject duplicate keys / invalid UTF-8) — scoped as a follow-on, behind compatibility verification.
- Refine the existing `make modernize` / `make fix` targets for the Go 1.27 modernizer set (new `atomictypes`/`embedlit`/`slicesbackward`/`unsafefuncs`, removed `fmtappendf`, renamed `waitgroup`→`waitgroupgo`); close the `make fix` gap so it actually runs `go fix ./...`, and apply the one-time modernizer diff surfaced by the toolchain bump.

## Capabilities

### New Capabilities
- `goroutine-leak-detection`: The backend continuously exposes a goroutine leak profile and raises an alert when goroutines are detected permanently blocked on concurrency primitives, catching silent consumer/RPC wedges that backlog-stall and liveness signals can miss.

### Modified Capabilities
<!-- None. The Go 1.27 toolchain bump, stdlib uuid migration, json/v2 adoption, and
     modernize target tuning change implementation and tooling only — no externally
     observable spec-level behavior changes. UUIDs remain V7 with identical string
     format; JSON wire behavior is unchanged unless the optional strict-parsing
     follow-on is pursued, which would be scoped as its own change. -->

## Impact

- **Code**: `backend/go.mod` (toolchain + `go` directive, drop `github.com/google/uuid`); 14 UUID call sites across ~11 files (`internal/usecase/*`, `internal/infrastructure/database/rdb/*`, `internal/infrastructure/messaging/cloudevents.go`, `internal/infrastructure/analytics/posthog/posthog_client.go`) routed through `internal/entity` ID helper; a new pprof/monitoring wiring point for the goroutine leak profile.
- **Dependencies**: `github.com/google/uuid v1.6.0` removed from direct requires (transitive `lithammer/shortuuid` unaffected). No new third-party dependency added.
- **Tooling/CI**: `make modernize` (already gates on `go fix -diff`) and `make fix` updated for the 1.27 modernizer set; `go test` gains the default `stdversion` vet check. Toolchain bump must land the one-time `go fix ./...` diff in the same change.
- **Ops/Infra**: new alert policy / monitoring hook for the goroutine leak profile (aligns with existing `app-error-log-alerting`, `jetstream-consumer-reliability` observability). No API, proto, or frontend impact.
- **Sequencing**: stdlib `uuid` adoption depends on the `go` directive reaching `1.27` first (the `stdversion` vet check enforces it).
