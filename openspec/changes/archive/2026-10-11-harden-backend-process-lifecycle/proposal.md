## Why

Backend processes stop serving, or fail silently, whenever a dependency is briefly unavailable, and nothing in the specs says they must not:

- Every binary exits within a second of start when NATS, Zitadel or the database is briefly unreachable. Prod NATS is a single pod on Spot nodes, so any node upgrade, consolidation or preemption that moves it causes a crash loop.
  - This happened 5 times between 2026-10-06 and 2026-10-10.
  - In the last 7 days, 45 startups failed: 29 on NATS, 11 on Zitadel discovery, 5 on the DB ping.
  - Startup used to wait for NATS. The wait was lost when `EnsureStreams` was removed in backend#423. It had been recorded only in an archived design, so nothing protected it.
- Startup and fatal errors are written as plain text on stdout. Cloud Logging stores them as INFO, so no ERROR-log alert fired for any of the 45 startup failures. Two harmless conditions would be logged as ERROR once the format is fixed: a normal health-server stop, and a shutdown after a failed start.
- The health checks contribute to DB outages.
  - API liveness and readiness both ping the database through the application pool. On 2026-10-09, a slow database made overlapping probes fill every API pool to its maximum for 30 minutes and exhaust the Cloud SQL connection slots.
  - Liveness also restarts healthy processes when a dependency is slow.
  - The event consumer's liveness restarts the pod after about 100 s of NATS disconnection, although the connection reconnects on its own.

These guarantees are about how every backend process behaves, so they belong in the specs, where a later refactor cannot remove them unnoticed.

## What Changes

- A backend process keeps running when NATS, Zitadel or the database is briefly unreachable at startup:
  - It waits for the dependencies it needs before doing work, or it defers them to first use.
  - It reports their state through readiness and logs.
  - It gives up only after a bounded wait.
- Zitadel clients are built without network I/O. A Zitadel outage fails only the calls that use Zitadel, and leaves startup and other calls unaffected.
- Liveness reports only whether the process itself can make progress. Readiness reports whether required dependencies are reachable.
  - Health checks never grow the database pool. Concurrent checks share one in-flight database check and reuse a short-lived result.
  - The event consumer is no longer restarted for a NATS disconnection that is reconnecting. It is still restarted when it is connected but not consuming (the 2026-07 wedge).
- Every log line from a deployed backend process, including startup and fatal errors, is single-line JSON carrying its severity. Normal shutdown and a shutdown after a failed start are not logged as errors.
- Spec tree: a new slot `components/infrastructure/backend/process/<component>` for rules that apply to every backend process (API servers, event consumers, jobs). `scripts/check-spec-layout.py` and the spec tree in `openspec/config.yaml` are updated to allow it.

## Capabilities

### New Capabilities

- `components/infrastructure/backend/process/startup-dependencies`: how a backend process treats NATS, Zitadel and the database while it starts: wait or defer, a bounded budget, and no exit on a transient outage.
- `components/infrastructure/backend/process/health-probes`: what liveness and readiness report for API servers and event consumers, and that health checks never add database connections.
- `components/infrastructure/backend/process/structured-logging`: the log format every deployed backend process emits, and which conditions are not errors.

### Modified Capabilities

None. The Zitadel-backed operations (`components/entity/user/delete-identity`, `components/entity/organizer/provision-tenant`) already fail with Internal when the sign-in service step fails. With Zitadel deferred to first use, an outage surfaces through that same path, so their requirements do not change.

## Impact

- **backend**:
  - `cmd/**/main.go` (bootstrap logger, shutdown handling)
  - `internal/di/*` (startup order and logger construction)
  - `internal/infrastructure/messaging` (publisher connect options, `connectWithRetry`, consumer health)
  - `internal/infrastructure/zitadel` (token source without discovery)
  - `internal/adapter/rpc/health_handler.go` (liveness service, coalesced readiness)
  - `pkg/shutdown`
  - a lint rule against package-level `slog`
- **cloud-provisioning**: the gRPC liveness probes of fan-api, admin-console-api, organizer-console-api and reception-api name the liveness service. Readiness and the Gateway health checks are unchanged.
- **specification**: `scripts/check-spec-layout.py` and the `context` spec tree in `openspec/config.yaml`.
- **Issues**: backend#584, backend#586 and backend#588. cloud-provisioning#624 (pool caps) and cloud-provisioning#625 (alert coverage) are separate and depend on this change.
